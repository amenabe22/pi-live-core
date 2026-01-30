from sqlalchemy import (
    Column, ForeignKey, Integer, String, Numeric, select,
    Text, Boolean, Date, DateTime, func, text
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, column_property, foreign
from core.db import Base

class Profile(Base):
    __tablename__ = "profile"

    user_id: int = Column(
        String(length=36),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    name: str | None = Column(
        Text,
        nullable=True,
    )
    dob: Date | None = Column(
        Date,
        nullable=True,
    )
    gender: str | None = Column(
        Text,
        nullable=True,
    )

    profile_picture = Column(
        Text, 
        nullable=True
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

    customer = relationship("Customer", back_populates="profile", uselist=False)
    driver   = relationship("Driver",   back_populates="profile", uselist=False)