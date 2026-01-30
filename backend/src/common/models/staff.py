from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, Boolean, Date, DateTime, func, text
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from core.db import Base


class Staff(Base):
    __tablename__ = "staff"

    user_id: int = Column(
        String(length=36),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    full_name: str | None = Column(
        Text,
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
