import uuid
from sqlalchemy import (
    Column, String, ForeignKey, Enum, DateTime, Float, Integer, func
)
from sqlalchemy.orm import relationship
import enum
from core.db import Base


class HistoryStatus(str, enum.Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TravelHistory(Base):
    __tablename__ = "travel_history"
    __table_args__ = {"schema": "public"}

    id = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    travel_id = Column(String(length=36), ForeignKey("public.travels.id"), unique=True, nullable=False)
    vehicle_id = Column(String(length=36), ForeignKey("public.vehicles.id"), nullable=False)
    driver_id = Column(String(length=36), ForeignKey("auth.users.id"), nullable=False)
    origin_station_id = Column(String(length=36), ForeignKey("public.stations.id"), nullable=False)
    destination_station_id = Column(String(length=36), ForeignKey("public.stations.id"), nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=True)
    distance_km = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    status = Column(Enum(HistoryStatus), nullable=False, default=HistoryStatus.COMPLETED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    travel = relationship("Travel", back_populates="history")
    vehicle = relationship("Vehicle", backref="history")
    driver = relationship("User", foreign_keys=[driver_id], backref="travel_history")
    origin_station = relationship("Station", foreign_keys=[origin_station_id])
    destination_station = relationship("Station", foreign_keys=[destination_station_id])
