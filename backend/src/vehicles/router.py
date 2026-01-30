from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from auth.simple.security import get_current_user, require_role, get_db
from auth.simple.schemas import UserRole
from common.models import Vehicle, User, VehicleStatus
from .schemas import VehicleCreate, VehicleUpdate, VehicleResponse

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new vehicle (Admin only)"""
    # Check if plate number already exists
    existing_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == vehicle_data.plate_number).first()
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this plate number already exists"
        )
    
    # Validate driver exists if driver_id is provided
    if vehicle_data.driver_id:
        driver = db.query(User).filter(User.id == vehicle_data.driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        # Check if user has driver role
        if UserRole.DRIVER.value not in driver.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a driver"
            )
    
    new_vehicle = Vehicle(**vehicle_data.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    
    return new_vehicle


@router.get("", response_model=List[VehicleResponse])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    status_filter: VehicleStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all vehicles"""
    query = db.query(Vehicle)
    
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific vehicle by ID"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update a vehicle (Admin only)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check if plate number is being updated and already exists
    if vehicle_data.plate_number and vehicle_data.plate_number != vehicle.plate_number:
        existing = db.query(Vehicle).filter(Vehicle.plate_number == vehicle_data.plate_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this plate number already exists"
            )
    
    # Validate driver if being updated
    if vehicle_data.driver_id:
        driver = db.query(User).filter(User.id == vehicle_data.driver_id).first()
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
    
    # Update fields
    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a vehicle (Admin only)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    db.delete(vehicle)
    db.commit()
    
    return None
