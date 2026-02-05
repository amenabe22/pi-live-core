from pydantic import BaseModel, EmailStr, Field
from datetime import date

from core.const import Gender, Role
from core.types import PhoneNumber


class StaffSignUpRequest(BaseModel):
    """Name (full_name), gender, and dob fill profile/staff data."""
    email: EmailStr
    password: str | None = Field(default=None, min_length=8)
    full_name: str
    gender: Gender
    dob: date | None = None
    role: Role
    firebase_auth_token: str


class StaffBeforeVerifyAuthResponse(BaseModel):
    verification_token: str
    class Config:
        from_attributes = True

class StaffVerifyOTPRequest(BaseModel):
    verification_token: str
    firebase_auth_token: str

class StaffSignInRequest(BaseModel):
    email: EmailStr
    password: str

class StaffResponse(BaseModel):
    user_id: int
    full_name: str
    gender: Gender
    email: EmailStr
    dob: date | None = None
    phone_no: PhoneNumber | None = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    firebase_auth_token: str
    new_password: str


class BootstrapSuperAdminRequest(BaseModel):
    """Only works when no staff exist. Creates the first super admin. Name, gender, dob fill profile."""
    email: EmailStr
    full_name: str
    gender: Gender
    dob: date | None = None
    password: str | None = Field(default=None, min_length=8)
