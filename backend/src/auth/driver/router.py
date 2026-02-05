from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.dependencies import get_uow
from core.uow import UnitOfWork


from core.const import Gender

from ..dependencies import require_enduser, require_member
from ..schemas import (
    AuthResponse,
    EndUserSignUpRequest,
    EndUserSignInRequest,
    EndUserResponse,
    GoogleSignInRequest,
    CreateDriverRequest,
    CreateDriverResponse,
)

from .service import create_driver_by_email, authenticate_driver, authenticate_driver_google
from ..service import update_phone_number_enduser


router = APIRouter(prefix="/driver", tags=["driver-auth"])

@router.post(
    "/signup",
    response_model=CreateDriverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a driver by email (staff only). Provide driver email only."
)
def signup(
    req: CreateDriverRequest,
    _staff=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return create_driver_by_email(req, uow)

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in as driver (phone + Firebase) and receive a JWT"
)
def login(
    req: EndUserSignInRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    return authenticate_driver(req, uow)

@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Sign in with Google (driver)"
)
def sign_in_with_google(
    req: GoogleSignInRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    return authenticate_driver_google(req, uow)

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
    driver = uow.driver.get(user["id"])

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver."
        )        

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
    summary="Update driver phone number"
)
def update_self_phone_no(
    req: EndUserSignInRequest,
    user = Depends(require_enduser),
    uow: UnitOfWork = Depends(get_uow),
):
    return update_phone_number_enduser(req, user["id"], uow)