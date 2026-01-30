from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from auth.simple.security import get_current_user, get_db
from common.models import TravelHistory, User
from .schemas import TravelHistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/travels", response_model=List[TravelHistoryResponse])
def list_travel_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_id: Optional[str] = None,
    driver_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List travel history with optional filters"""
    query = db.query(TravelHistory)
    
    if vehicle_id:
        query = query.filter(TravelHistory.vehicle_id == vehicle_id)
    
    if driver_id:
        query = query.filter(TravelHistory.driver_id == driver_id)
    
    if status_filter:
        query = query.filter(TravelHistory.status == status_filter)
    
    if start_date:
        query = query.filter(TravelHistory.departure_time >= start_date)
    
    if end_date:
        query = query.filter(TravelHistory.departure_time <= end_date)
    
    # Order by most recent first
    query = query.order_by(TravelHistory.departure_time.desc())
    
    history = query.offset(skip).limit(limit).all()
    return history


@router.get("/travels/{history_id}", response_model=TravelHistoryResponse)
def get_travel_history(
    history_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific travel history record"""
    history = db.query(TravelHistory).filter(TravelHistory.id == history_id).first()
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel history not found"
        )
    return history


@router.get("/vehicle/{vehicle_id}", response_model=List[TravelHistoryResponse])
def get_vehicle_history(
    vehicle_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get travel history for a specific vehicle"""
    history = db.query(TravelHistory)\
        .filter(TravelHistory.vehicle_id == vehicle_id)\
        .order_by(TravelHistory.departure_time.desc())\
        .offset(skip).limit(limit).all()
    return history


@router.get("/driver/{driver_id}", response_model=List[TravelHistoryResponse])
def get_driver_history(
    driver_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get travel history for a specific driver"""
    history = db.query(TravelHistory)\
        .filter(TravelHistory.driver_id == driver_id)\
        .order_by(TravelHistory.departure_time.desc())\
        .offset(skip).limit(limit).all()
    return history
