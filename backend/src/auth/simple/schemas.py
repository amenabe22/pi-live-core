from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    DRIVER = "driver"
    USER = "user"
    ADMIN = "admin"
    DISPATCHER = "dispatcher"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    role: Optional[UserRole] = UserRole.USER


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None
