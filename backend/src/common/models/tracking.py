import uuid
from sqlalchemy import (
    Column, String, ForeignKey, DateTime, Float, func
)
from sqlalchemy.orm import relationship
from core.db import Base


class LiveTracking(Base):
    __tablename__ = "live_tracking"
    __table_args__ = {"schema": "public"}

    id = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    vehicle_id = Column(String(length=36), ForeignKey("public.vehicles.id"), nullable=False, index=True)
    driver_id = Column(String(length=36), ForeignKey("auth.users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)  # km/h
    heading = Column(Float, nullable=True)  # degrees (0-360)
    accuracy = Column(Float, nullable=True)  # meters
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vehicle = relationship("Vehicle", backref="tracking_points")
    driver = relationship("User", foreign_keys=[driver_id], backref="tracking_points")
