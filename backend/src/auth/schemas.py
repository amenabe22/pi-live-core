from pydantic import BaseModel, EmailStr, Field
from datetime import date

from core.const import Gender, Role
from core.types import PhoneNumber


class AuthResponse(BaseModel):
    user_id: str
    access_token: str
    token_type: str
    class Config:
        from_attributes = True

class EndUserSignUpRequest(BaseModel):
    phone_no: PhoneNumber
    password: str = Field(..., min_length=8)
    name: str
    gender: Gender
    dob: date
    firebase_auth_token: str

class EndUserSignInRequest(BaseModel):
    firebase_auth_token: str

class EndUserResponse(BaseModel):
    user_id: str
    name: str
    gender: Gender
    phone_no: PhoneNumber
    dob: date
    profile_picture: str | None

    class Config:
        from_attributes = True

class EndUserPhoneNoUpdate(BaseModel):
    firebase_auth_token: str

