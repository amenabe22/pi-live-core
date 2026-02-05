from typing import Dict, Any

from fastapi import (
    APIRouter, Depends, HTTPException, 
    status, Form, File, UploadFile
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.dependencies import get_uow
from core.uow import UnitOfWork

from core.const import Gender

from ..dependencies import require_enduser
from ..schemas import (
    AuthResponse,
    EndUserSignUpRequest,
    EndUserSignInRequest,
    EndUserResponse,
    EndUserPhoneNoUpdate,
    GoogleSignInRequest,
)

from .service import create_customer, authenticate_customer, authenticate_customer_google
from ..service import update_phone_number_enduser


router = APIRouter(prefix="/customer", tags=["customer-auth"])

@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up for customer"
)
def signup(
    req: EndUserSignUpRequest,
    uow: UnitOfWork = Depends(get_uow)
):
    return create_customer(req, uow)

@router.post(
    "/login", 
    response_model=AuthResponse,
    summary="Log in as customer and receive a JWT"
)
def login(
    req: EndUserSignInRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    return authenticate_customer(req, uow)

@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Sign in with Google (customer)"
)
def sign_in_with_google(
    req: GoogleSignInRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    return authenticate_customer_google(req, uow)

@router.get(
    "/me", 
    response_model=EndUserResponse,
    summary="Get current account detail"
)
def read_own_profile(
    user=Depends(require_enduser),
    uow: UnitOfWork = Depends(get_uow),
):
    profiles = uow.profile.get(user["id"])
    usering = uow.users.get(user["id"])

    return EndUserResponse(
        user_id   = profiles.user_id,
        name      = profiles.name,
        gender    = Gender(profiles.gender),
        phone_no  = usering.phone_no,
        dob       = profiles.dob,
        profile_picture = profiles.profile_picture
    )


@router.put(
    "/phone-no", 
    response_model=EndUserResponse,
    summary="Update customer phone number"
)
def update_self_phone_no(
    req: EndUserSignInRequest,
    user = Depends(require_enduser),
    uow: UnitOfWork = Depends(get_uow),
):
    return update_phone_number_enduser(req, user["id"], uow)