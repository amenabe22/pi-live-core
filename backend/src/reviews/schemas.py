from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from common.models import ReviewType


class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    travel_id: Optional[str] = None
    driver_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    review_type: Optional[ReviewType] = ReviewType.TRIP


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """Schema for review response"""
    id: str
    travel_id: Optional[str] = None
    driver_id: str
    reviewer_id: str
    rating: int
    comment: Optional[str] = None
    review_type: ReviewType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DriverStatsResponse(BaseModel):
    """Schema for driver rating statistics"""
    driver_id: str
    average_rating: float
    total_reviews: int
    rating_breakdown: Dict[int, int] = {}
