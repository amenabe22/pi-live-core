from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from auth.simple.security import get_current_user, require_role, get_db
from auth.simple.schemas import UserRole
from common.models import Review, User, Travel
from .schemas import ReviewCreate, ReviewUpdate, ReviewResponse, DriverStatsResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review"""
    # Validate driver exists
    driver = db.query(User).filter(User.id == review_data.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if UserRole.DRIVER.value not in driver.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a driver"
        )
    
    # Validate travel exists if provided
    if review_data.travel_id:
        travel = db.query(Travel).filter(Travel.id == review_data.travel_id).first()
        if not travel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel not found"
            )
        
        # Check if user already reviewed this travel
        existing = db.query(Review).filter(
            Review.travel_id == review_data.travel_id,
            Review.reviewer_id == current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this travel"
            )
    
    new_review = Review(
        **review_data.model_dump(),
        reviewer_id=current_user.id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return new_review


@router.get("", response_model=List[ReviewResponse])
def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    driver_id: Optional[str] = None,
    travel_id: Optional[str] = None,
    rating: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List reviews with optional filters"""
    query = db.query(Review)
    
    if driver_id:
        query = query.filter(Review.driver_id == driver_id)
    
    if travel_id:
        query = query.filter(Review.travel_id == travel_id)
    
    if rating:
        query = query.filter(Review.rating == rating)
    
    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return review


@router.get("/driver/{driver_id}/stats", response_model=DriverStatsResponse)
def get_driver_stats(
    driver_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get driver rating statistics"""
    driver = db.query(User).filter(User.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Get average rating and total count
    stats = db.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('total_reviews')
    ).filter(Review.driver_id == driver_id).first()
    
    # Get rating breakdown
    breakdown = db.query(
        Review.rating,
        func.count(Review.id).label('count')
    ).filter(Review.driver_id == driver_id).group_by(Review.rating).all()
    
    rating_breakdown = {rating: count for rating, count in breakdown}
    
    return DriverStatsResponse(
        driver_id=driver_id,
        average_rating=float(stats.avg_rating) if stats.avg_rating else 0.0,
        total_reviews=stats.total_reviews or 0,
        rating_breakdown=rating_breakdown
    )


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review (only by the reviewer)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    # Update fields
    for field, value in review_data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a review (Admin only)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    db.delete(review)
    db.commit()
    
    return None
