import uuid
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, Boolean, Date, DateTime, func, text
)
from sqlalchemy.dialects.postgresql import ARRAY
from core.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: str = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    email: str | None = Column(
        String(length=255),
        unique=True,
        nullable=True,
        index=True,
    )
    password: str | None = Column(
        String(length=255),
        nullable=True,
    )
    phone_no: str | None = Column(
        String(length=20),
        unique=True,
        nullable=True,
    )
    is_otp_verified: bool = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    roles: list[str] = Column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default=text("ARRAY[]::text[]")
    )

    is_suspended: bool = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )
    suspended_by: int | None = Column(
        String(length=36),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
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