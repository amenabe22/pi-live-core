from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StationBase(BaseModel):
    """Base station schema"""
    name: str
    latitude: float
    longitude: float
    radius: Optional[float] = 100.0
    address: Optional[str] = None


class StationCreate(StationBase):
    """Schema for station creation"""
    pass


class StationUpdate(BaseModel):
    """Schema for station update"""
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = None
    address: Optional[str] = None


class StationResponse(StationBase):
    """Schema for station response"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleAtStationCheck(BaseModel):
    """Schema for vehicle at station check"""
    vehicle_id: str
    is_at_station: bool
    station_id: Optional[str] = None
    station_name: Optional[str] = None
    distance_meters: Optional[float] = None
