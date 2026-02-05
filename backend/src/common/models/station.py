import uuid
from sqlalchemy import (
    Column, ForeignKey, Integer, String, Float,
    Text, Boolean, Date, DateTime, func, text
)
from sqlalchemy.dialects.postgresql import ARRAY
from core.db import Base


class Station(Base):
    __tablename__ = "station"

    id: str = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    name: str = Column(
        String(length=1024),
        nullable=False,
    )

    address: str = Column(
        String(length=1024), 
        nullable=False
    )
    latitude: float = Column(
        Float,
        nullable=False
    )
    longitude: float = Column(
        Float, 
        nullable=False
    )

    created_by: int | None = Column(
        String(length=36),
        ForeignKey("staff.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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
