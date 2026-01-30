from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, Boolean, Date, DateTime, func, text
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from core.db import Base


class Customer(Base):
    __tablename__ = "customer"

    profile_id: int = Column(
        String(length=36),
        ForeignKey("profile.user_id", ondelete="CASCADE"),
        primary_key=True,
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

    profile = relationship(
        "Profile",
        back_populates="customer",
        uselist=False,
        primaryjoin="Customer.profile_id==Profile.user_id",
    )