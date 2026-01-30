from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timedelta

from auth.simple.security import get_current_user, get_db
from common.models import LiveTracking, Vehicle, Travel, User
from .schemas import LiveTrackingResponse, RouteResponse, LiveTrackingCreate, RoutePoint

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.get("/vehicle/{vehicle_id}/current", response_model=LiveTrackingResponse)
def get_current_tracking(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest tracking point for a vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    tracking = db.query(LiveTracking)\
        .filter(LiveTracking.vehicle_id == vehicle_id)\
        .order_by(desc(LiveTracking.timestamp))\
        .first()
    
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tracking data found for this vehicle"
        )
    
    return tracking


@router.get("/vehicle/{vehicle_id}/history", response_model=List[LiveTrackingResponse])
def get_tracking_history(
    vehicle_id: str,
    start_time: Optional[datetime] = Query(None, description="Start time for tracking history"),
    end_time: Optional[datetime] = Query(None, description="End time for tracking history"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of points to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tracking history for a vehicle within a time range"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    query = db.query(LiveTracking).filter(LiveTracking.vehicle_id == vehicle_id)
    
    # Default to last 24 hours if no time range specified
    if not start_time:
        start_time = datetime.utcnow() - timedelta(hours=24)
    if not end_time:
        end_time = datetime.utcnow()
    
    query = query.filter(
        LiveTracking.timestamp >= start_time,
        LiveTracking.timestamp <= end_time
    )
    
    tracking_points = query.order_by(LiveTracking.timestamp.asc()).limit(limit).all()
    
    return tracking_points


@router.get("/vehicle/{vehicle_id}/route", response_model=RouteResponse)
def get_route(
    vehicle_id: str,
    travel_id: Optional[str] = Query(None, description="Filter by specific travel"),
    start_time: Optional[datetime] = Query(None, description="Start time for route"),
    end_time: Optional[datetime] = Query(None, description="End time for route"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get route path for a vehicle, optionally filtered by travel"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    query = db.query(LiveTracking).filter(LiveTracking.vehicle_id == vehicle_id)
    
    if travel_id:
        # Validate travel exists and belongs to vehicle
        travel = db.query(Travel).filter(
            Travel.id == travel_id,
            Travel.vehicle_id == vehicle_id
        ).first()
        if not travel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel not found for this vehicle"
            )
        
        # Use travel time range
        if travel.actual_departure and travel.actual_arrival:
            query = query.filter(
                LiveTracking.timestamp >= travel.actual_departure,
                LiveTracking.timestamp <= travel.actual_arrival
            )
        elif travel.scheduled_departure and travel.scheduled_arrival:
            query = query.filter(
                LiveTracking.timestamp >= travel.scheduled_departure,
                LiveTracking.timestamp <= travel.scheduled_arrival
            )
    else:
        # Use provided time range or default to last 24 hours
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        query = query.filter(
            LiveTracking.timestamp >= start_time,
            LiveTracking.timestamp <= end_time
        )
    
    tracking_points = query.order_by(LiveTracking.timestamp.asc()).all()
    
    if not tracking_points:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tracking data found for the specified criteria"
        )
    
    route_points = [
        RoutePoint(
            latitude=point.latitude,
            longitude=point.longitude,
            timestamp=point.timestamp,
            speed=point.speed
        )
        for point in tracking_points
    ]
    
    return RouteResponse(
        vehicle_id=vehicle_id,
        travel_id=travel_id,
        points=route_points,
        total_points=len(route_points),
        start_time=tracking_points[0].timestamp,
        end_time=tracking_points[-1].timestamp
    )


@router.post("", response_model=LiveTrackingResponse, status_code=status.HTTP_201_CREATED)
def create_tracking_point(
    tracking_data: LiveTrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually store a tracking point (backup to WebSocket)"""
    # Validate vehicle exists
    vehicle = db.query(Vehicle).filter(Vehicle.id == tracking_data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Validate driver exists
    driver = db.query(User).filter(User.id == tracking_data.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    new_tracking = LiveTracking(**tracking_data.model_dump())
    db.add(new_tracking)
    db.commit()
    db.refresh(new_tracking)
    
    return new_tracking
