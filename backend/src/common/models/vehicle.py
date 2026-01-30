import uuid
from sqlalchemy import (
    Column, String, Float, ForeignKey, Enum, DateTime, Integer, Text, func
)
from sqlalchemy.orm import relationship
import enum
from core.db import Base


class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = {"schema": "public"}

    id = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    plate_number = Column(String, unique=True, index=True, nullable=False)
    model = Column(String, nullable=False)
    status = Column(Enum(VehicleStatus), nullable=False, default=VehicleStatus.ACTIVE)
    driver_id = Column(String(length=36), ForeignKey("auth.users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    driver = relationship("User", foreign_keys=[driver_id], backref="vehicles")
