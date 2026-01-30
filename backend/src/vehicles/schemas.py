from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from common.models import VehicleStatus


class VehicleBase(BaseModel):
    """Base vehicle schema"""
    plate_number: str
    model: str
    status: Optional[VehicleStatus] = VehicleStatus.ACTIVE
    driver_id: Optional[str] = None


class VehicleCreate(VehicleBase):
    """Schema for vehicle creation"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for vehicle update"""
    plate_number: Optional[str] = None
    model: Optional[str] = None
    status: Optional[VehicleStatus] = None
    driver_id: Optional[str] = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
