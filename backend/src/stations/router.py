from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import math
import json

from fastapi import Request
from auth.simple.security import get_current_user, require_role, get_db
from auth.simple.schemas import UserRole
from common.models import Station, User
from core.dependencies import get_redis
from .schemas import StationCreate, StationUpdate, StationResponse, VehicleAtStationCheck

router = APIRouter(prefix="/stations", tags=["stations"])


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two coordinates using the Haversine formula.
    Returns distance in meters.
    """
    R = 6371000  # Earth's radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


@router.post("", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
def create_station(
    station_data: StationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new station (Admin only)"""
    new_station = Station(**station_data.model_dump())
    db.add(new_station)
    db.commit()
    db.refresh(new_station)
    
    return new_station


@router.get("", response_model=List[StationResponse])
def list_stations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all stations"""
    stations = db.query(Station).offset(skip).limit(limit).all()
    return stations


@router.get("/{station_id}", response_model=StationResponse)
def get_station(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific station by ID"""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    return station


@router.put("/{station_id}", response_model=StationResponse)
def update_station(
    station_id: str,
    station_data: StationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update a station (Admin only)"""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    # Update fields
    for field, value in station_data.model_dump(exclude_unset=True).items():
        setattr(station, field, value)
    
    db.commit()
    db.refresh(station)
    
    return station


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a station (Admin only)"""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    db.delete(station)
    db.commit()
    
    return None


@router.get("/check/{vehicle_id}/at-station", response_model=VehicleAtStationCheck)
def check_vehicle_at_station(
    vehicle_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a vehicle is currently at any station based on its real-time location.
    Uses Redis to get current vehicle location and calculates distance to all stations.
    """
    # Get vehicle's current location from Redis
    redis_client = get_redis(request)
    location_key = f"vehicle:{vehicle_id}:location"
    location_data = redis_client.get(location_key)
    
    if not location_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle location not found. Vehicle may not have sent location data yet."
        )
    
    try:
        location = json.loads(location_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid location data format"
        )
    
    vehicle_lat = location.get("latitude")
    vehicle_lon = location.get("longitude")
    
    if vehicle_lat is None or vehicle_lon is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle location data"
        )
    
    # Get all stations
    stations = db.query(Station).all()
    
    # Check distance to each station
    closest_station = None
    closest_distance = float('inf')
    
    for station in stations:
        distance = calculate_distance(
            vehicle_lat, vehicle_lon,
            station.latitude, station.longitude
        )
        
        # Check if vehicle is within station's radius
        if distance <= station.radius and distance < closest_distance:
            closest_station = station
            closest_distance = distance
    
    if closest_station:
        return VehicleAtStationCheck(
            vehicle_id=vehicle_id,
            is_at_station=True,
            station_id=closest_station.id,
            station_name=closest_station.name,
            distance_meters=closest_distance
        )
    else:
        return VehicleAtStationCheck(
            vehicle_id=vehicle_id,
            is_at_station=False
        )
