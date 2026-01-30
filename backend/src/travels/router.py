from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from auth.simple.security import get_current_user, require_role, get_db
from auth.simple.schemas import UserRole
from common.models import Travel, Vehicle, User, Station, TravelStatus
from .schemas import TravelCreate, TravelUpdate, TravelResponse

router = APIRouter(prefix="/travels", tags=["travels"])


@router.post("", response_model=TravelResponse, status_code=status.HTTP_201_CREATED)
def create_travel(
    travel_data: TravelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.USER]))
):
    """Create a new travel/trip"""
    # Validate vehicle exists
    vehicle = db.query(Vehicle).filter(Vehicle.id == travel_data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Validate driver exists and is a driver
    driver = db.query(User).filter(User.id == travel_data.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    if UserRole.DRIVER.value not in driver.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a driver"
        )
    
    # Validate stations exist
    origin = db.query(Station).filter(Station.id == travel_data.origin_station_id).first()
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Origin station not found"
        )
    
    destination = db.query(Station).filter(Station.id == travel_data.destination_station_id).first()
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination station not found"
        )
    
    # Check if origin and destination are the same
    if travel_data.origin_station_id == travel_data.destination_station_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Origin and destination stations cannot be the same"
        )
    
    new_travel = Travel(**travel_data.model_dump())
    db.add(new_travel)
    db.commit()
    db.refresh(new_travel)
    
    return new_travel


@router.get("", response_model=List[TravelResponse])
def list_travels(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[TravelStatus] = None,
    vehicle_id: Optional[str] = None,
    driver_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List travels with optional filters"""
    query = db.query(Travel)
    
    if status_filter:
        query = query.filter(Travel.status == status_filter)
    
    if vehicle_id:
        query = query.filter(Travel.vehicle_id == vehicle_id)
    
    if driver_id:
        query = query.filter(Travel.driver_id == driver_id)
    
    travels = query.offset(skip).limit(limit).all()
    return travels


@router.get("/{travel_id}", response_model=TravelResponse)
def get_travel(
    travel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific travel by ID"""
    travel = db.query(Travel).filter(Travel.id == travel_id).first()
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel not found"
        )
    return travel


@router.put("/{travel_id}", response_model=TravelResponse)
def update_travel(
    travel_id: str,
    travel_data: TravelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a travel"""
    travel = db.query(Travel).filter(Travel.id == travel_id).first()
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel not found"
        )
    
    # Update fields
    for field, value in travel_data.model_dump(exclude_unset=True).items():
        setattr(travel, field, value)
    
    db.commit()
    db.refresh(travel)
    
    return travel


@router.post("/{travel_id}/start", response_model=TravelResponse)
def start_travel(
    travel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a travel as started (in progress)"""
    travel = db.query(Travel).filter(Travel.id == travel_id).first()
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel not found"
        )
    
    if travel.status != TravelStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start travel with status: {travel.status}"
        )
    
    travel.status = TravelStatus.IN_PROGRESS
    travel.actual_departure = datetime.utcnow()
    
    db.commit()
    db.refresh(travel)
    
    return travel


@router.post("/{travel_id}/complete", response_model=TravelResponse)
def complete_travel(
    travel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a travel as completed"""
    travel = db.query(Travel).filter(Travel.id == travel_id).first()
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel not found"
        )
    
    if travel.status != TravelStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete travel with status: {travel.status}"
        )
    
    travel.status = TravelStatus.COMPLETED
    travel.actual_arrival = datetime.utcnow()
    
    db.commit()
    db.refresh(travel)
    
    return travel


@router.post("/{travel_id}/cancel", response_model=TravelResponse)
def cancel_travel(
    travel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.USER]))
):
    """Cancel a travel"""
    travel = db.query(Travel).filter(Travel.id == travel_id).first()
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel not found"
        )
    
    if travel.status == TravelStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed travel"
        )
    
    travel.status = TravelStatus.CANCELLED
    
    db.commit()
    db.refresh(travel)
    
    return travel


@router.delete("/{travel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_travel(
    travel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a travel (Admin only)"""
    travel = db.query(Travel).filter(Travel.id == travel_id).first()
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel not found"
        )
    
    db.delete(travel)
    db.commit()
    
    return None
