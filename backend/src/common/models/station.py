import uuid
from sqlalchemy import (
    Column, String, Float, DateTime, func, Text
)
from sqlalchemy.orm import relationship
from core.db import Base


class Station(Base):
    __tablename__ = "stations"
    __table_args__ = {"schema": "public"}

    id = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, default=100.0)  # Radius in meters to consider "at station"
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    origin_travels = relationship("Travel", foreign_keys="[Travel.origin_station_id]", back_populates="origin_station")
    destination_travels = relationship("Travel", foreign_keys="[Travel.destination_station_id]", back_populates="destination_station")
