import uuid
from sqlalchemy import (
    Column, String, ForeignKey, Enum, DateTime, Integer, Text, func
)
from sqlalchemy.orm import relationship
import enum
from core.db import Base


class ReviewType(str, enum.Enum):
    DRIVER = "driver"
    TRIP = "trip"
    SERVICE = "service"


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"schema": "public"}

    id = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    travel_id = Column(String(length=36), ForeignKey("public.travels.id"), nullable=True)
    driver_id = Column(String(length=36), ForeignKey("auth.users.id"), nullable=False)
    reviewer_id = Column(String(length=36), ForeignKey("auth.users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    review_type = Column(Enum(ReviewType), nullable=False, default=ReviewType.TRIP)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    travel = relationship("Travel", back_populates="reviews")
    driver = relationship("User", foreign_keys=[driver_id], backref="driver_reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], backref="reviews_given")
