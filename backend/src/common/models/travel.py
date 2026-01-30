import uuid
from sqlalchemy import (
    Column, String, ForeignKey, Enum, DateTime, Float, Text, func
)
from sqlalchemy.orm import relationship
import enum
from core.db import Base


class TravelStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Travel(Base):
    __tablename__ = "travels"
    __table_args__ = {"schema": "public"}

    id = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    vehicle_id = Column(String(length=36), ForeignKey("public.vehicles.id"), nullable=False)
    driver_id = Column(String(length=36), ForeignKey("auth.users.id"), nullable=False)
    origin_station_id = Column(String(length=36), ForeignKey("public.stations.id"), nullable=False)
    destination_station_id = Column(String(length=36), ForeignKey("public.stations.id"), nullable=False)
    status = Column(Enum(TravelStatus), nullable=False, default=TravelStatus.SCHEDULED)
    scheduled_departure = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    distance = Column(Float, nullable=True)  # Distance in kilometers
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    vehicle = relationship("Vehicle", backref="travels")
    driver = relationship("User", foreign_keys=[driver_id], backref="driven_travels")
    origin_station = relationship("Station", foreign_keys=[origin_station_id], back_populates="origin_travels")
    destination_station = relationship("Station", foreign_keys=[destination_station_id], back_populates="destination_travels")
    history = relationship("TravelHistory", back_populates="travel", uselist=False)
    reviews = relationship("Review", back_populates="travel")
