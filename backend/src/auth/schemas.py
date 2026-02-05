from pydantic import BaseModel, EmailStr, Field, model_validator
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
    phone_no: PhoneNumber | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    name: str
    gender: Gender
    dob: date
    firebase_auth_token: str | None = None

    @model_validator(mode="after")
    def phone_or_email(self):
        if self.phone_no is None and self.email is None:
            raise ValueError("Provide either phone_no or email")
        if self.phone_no is not None and self.firebase_auth_token is None:
            raise ValueError("firebase_auth_token required when signing up with phone")
        return self

class EndUserSignInRequest(BaseModel):
    firebase_auth_token: str

class GoogleSignInRequest(BaseModel):
    firebase_id_token: str

class EndUserResponse(BaseModel):
    user_id: str
    name: str
    gender: Gender
    phone_no: PhoneNumber | None = None
    dob: date
    profile_picture: str | None

    class Config:
        from_attributes = True

class EndUserPhoneNoUpdate(BaseModel):
    firebase_auth_token: str


class CreateDriverRequest(BaseModel):
    email: EmailStr
    name: str
    gender: Gender | None = None
    dob: date | None = None
    password: str | None = Field(default=None, min_length=8)


class CreateDriverResponse(BaseModel):
    user_id: str
    email: str

