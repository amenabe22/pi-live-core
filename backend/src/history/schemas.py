from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from common.models import HistoryStatus


class TravelHistoryResponse(BaseModel):
    """Schema for travel history response"""
    id: str
    travel_id: str
    vehicle_id: str
    driver_id: str
    origin_station_id: str
    destination_station_id: str
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    status: HistoryStatus
    created_at: datetime

    class Config:
        from_attributes = True
