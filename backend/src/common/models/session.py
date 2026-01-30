from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    Index,
    func,
    text,
)
from core.db import Base
from datetime import datetime
import uuid

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_auth_sessions_active", "id", "revoked", "expires_at"),
        {"schema": "auth"},
    )

    id: str = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: int = Column(
        String(length=36),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    revoked: bool = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    revoked_at: datetime | None = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
