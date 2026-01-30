import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from auth.simple.security import verify_token, get_db
from auth.simple.schemas import UserRole
from common.models import User, LiveTracking, Vehicle
from services.websocket_manager import manager

router = APIRouter(tags=["websocket"])


class LocationUpdate(BaseModel):
    """Location update schema"""
    latitude: float
    longitude: float
    speed: float = None
    heading: float = None
    accuracy: float = None
    timestamp: str = None


async def get_user_from_token(token: str, db: Session) -> User:
    """Verify JWT token and return user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    try:
        token_data = verify_token(token, credentials_exception)
        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


@router.websocket("/ws/track/{vehicle_id}")
async def track_websocket(
    websocket: WebSocket,
    vehicle_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for dashboards to subscribe to vehicle location updates.
    Requires JWT token in query parameter.
    """
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Verify JWT token and get user
        user = await get_user_from_token(token, db)
        
        # Connect to WebSocket
        await manager.connect(websocket, vehicle_id)
        
        # Subscribe to Redis Pub/Sub channel for this vehicle
        await manager.subscribe_to_vehicle(vehicle_id)
        
        # Send confirmation
        await websocket.send_json({
            "status": "connected",
            "vehicle_id": vehicle_id,
            "message": "Tracking vehicle location updates"
        })
        
        # Keep connection alive and let the pubsub task handle broadcasting
        while True:
            try:
                # Just keep the connection alive
                # The pubsub listener will broadcast messages
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, vehicle_id)
    except HTTPException:
        await websocket.close()
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        try:
            next(db_gen, None)
        except StopIteration:
            pass


@router.websocket("/ws/driver/{vehicle_id}")
async def driver_websocket(
    websocket: WebSocket,
    vehicle_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for drivers to push GPS coordinates.
    Requires JWT token in query parameter and driver role.
    """
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Verify JWT token and get user
        user = await get_user_from_token(token, db)
        
        # Verify user is a driver
        if UserRole.DRIVER.value not in user.roles:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect to WebSocket
        await manager.connect(websocket, vehicle_id)
        
        # Send confirmation
        await websocket.send_json({
            "status": "connected",
            "vehicle_id": vehicle_id,
            "message": "Ready to receive location updates"
        })
        
        # Listen for location updates
        while True:
            try:
                # Receive JSON message with location data
                data = await websocket.receive_json()
                
                # Validate location data
                location = LocationUpdate(**data)
                
                # Update location in Redis and publish to Pub/Sub
                await manager.update_vehicle_location(
                    vehicle_id=vehicle_id,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    speed=location.speed,
                    heading=location.heading,
                    accuracy=location.accuracy,
                    timestamp=location.timestamp
                )
                
                # Store tracking point in database
                try:
                    # Get vehicle to ensure it exists
                    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
                    if vehicle:
                        # Parse timestamp if provided, otherwise use current time
                        track_timestamp = datetime.utcnow()
                        if location.timestamp:
                            try:
                                track_timestamp = datetime.fromisoformat(location.timestamp.replace('Z', '+00:00'))
                            except (ValueError, AttributeError):
                                pass
                        
                        tracking_point = LiveTracking(
                            vehicle_id=vehicle_id,
                            driver_id=user.id,
                            latitude=location.latitude,
                            longitude=location.longitude,
                            speed=location.speed,
                            heading=location.heading,
                            accuracy=location.accuracy,
                            timestamp=track_timestamp
                        )
                        db.add(tracking_point)
                        db.commit()
                except Exception as db_error:
                    # Log error but don't break the WebSocket connection
                    db.rollback()
                
                # Send acknowledgment
                await websocket.send_json({
                    "status": "received",
                    "vehicle_id": vehicle_id,
                    "latitude": location.latitude,
                    "longitude": location.longitude
                })
                
            except ValidationError as ve:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Invalid location data: {str(ve)}"
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "status": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                await websocket.send_json({
                    "status": "error",
                    "message": str(e)
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, vehicle_id)
    except HTTPException:
        await websocket.close()
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        try:
            next(db_gen, None)
        except StopIteration:
            pass
