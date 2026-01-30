from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_db,
)
from core.config import config
from common.models import User
from .schemas import UserCreate, UserResponse, Token, UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        roles=[user_data.role.value] if user_data.role else [UserRole.USER.value],
        is_otp_verified=True,  # Simple auth doesn't need OTP
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    role = new_user.roles[0] if new_user.roles else UserRole.USER.value
    return UserResponse(
        id=new_user.id,
        email=new_user.email or "",
        role=UserRole(role) if role in [r.value for r in UserRole] else UserRole.USER,
        created_at=new_user.created_at,
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password to get JWT token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.password or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is suspended
    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    role = user.roles[0] if user.roles else UserRole.USER.value
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": role
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    # Map roles list to single role for API response (frontend expects "role")
    role = current_user.roles[0] if current_user.roles else UserRole.USER.value
    return UserResponse(
        id=current_user.id,
        email=current_user.email or "",
        role=UserRole(role) if role in [r.value for r in UserRole] else UserRole.USER,
        created_at=current_user.created_at,
    )
