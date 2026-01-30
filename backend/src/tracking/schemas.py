from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class LiveTrackingBase(BaseModel):
    """Base tracking schema"""
    vehicle_id: str
    latitude: float
    longitude: float
    speed: Optional[float] = None
    heading: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime


class LiveTrackingCreate(LiveTrackingBase):
    """Schema for creating tracking point"""
    driver_id: str


class LiveTrackingResponse(LiveTrackingBase):
    """Schema for tracking response"""
    id: str
    driver_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoutePoint(BaseModel):
    """Schema for route point"""
    latitude: float
    longitude: float
    timestamp: datetime
    speed: Optional[float] = None


class RouteResponse(BaseModel):
    """Schema for route response"""
    vehicle_id: str
    travel_id: Optional[str] = None
    points: List[RoutePoint]
    total_points: int
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True
