from pydantic import BaseModel, EmailStr, Field
from datetime import date

from core.const import Gender, Role
from core.types import PhoneNumber


class StaffSignUpRequest(BaseModel):
    email: EmailStr
    phone_no: PhoneNumber
    password: str = Field(..., min_length=8)
    full_name: str
    gender: Gender
    type: str | None = None
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
    phone_no: PhoneNumber
    password: str

class StaffResponse(BaseModel):
    user_id: int
    full_name: str
    gender: Gender
    email: EmailStr
    phone_no: PhoneNumber
    type: str | None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    firebase_auth_token: str
    new_password: str
