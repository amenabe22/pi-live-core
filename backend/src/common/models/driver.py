from sqlalchemy import (
    Column, ForeignKey, Integer, String, Numeric,
    Text, Boolean, Date, DateTime, func, text
)
from decimal import Decimal
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from core.db import Base
from core.const import DriverStatus


class Driver(Base):
    __tablename__ = "driver"

    profile_id: int = Column(
        String(length=36),
        ForeignKey("profile.user_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    status: str = Column(
        String(length=20),
        nullable=False,
        server_default=DriverStatus.INACTIVE,
        index=True,
    )

    status_updated_at: DateTime = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: DateTime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: DateTime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    profile = relationship(
        "Profile",
        back_populates="driver",
        uselist=False,
        primaryjoin="Driver.profile_id==Profile.user_id",
    )
