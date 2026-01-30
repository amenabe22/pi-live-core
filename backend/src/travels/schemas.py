from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from common.models import TravelStatus


class TravelBase(BaseModel):
    """Base travel schema"""
    vehicle_id: str
    driver_id: str
    origin_station_id: str
    destination_station_id: str
    status: Optional[TravelStatus] = TravelStatus.SCHEDULED
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None
    distance: Optional[float] = None
    notes: Optional[str] = None


class TravelCreate(TravelBase):
    """Schema for travel creation"""
    pass


class TravelUpdate(BaseModel):
    """Schema for travel update"""
    status: Optional[TravelStatus] = None
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    distance: Optional[float] = None
    notes: Optional[str] = None


class TravelResponse(TravelBase):
    """Schema for travel response"""
    id: str
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
