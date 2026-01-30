from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.dependencies import get_uow
from core.uow import UnitOfWork

from ..dependencies import require_member, require_superadmin
from ..schemas import AuthResponse
from .schemas import (
    StaffSignUpRequest, StaffSignInRequest, StaffResponse,
    StaffBeforeVerifyAuthResponse, StaffVerifyOTPRequest,
    ChangePasswordRequest
)
from .service import ( 
    create_staff, get_verification_token, authenticate_staff,
    change_staff_password, change_own_password
)

router = APIRouter(prefix="/staff", tags=["staff-auth"])

@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new staff member"
)
def signup_staff(
    req: StaffSignUpRequest,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow)
):
    return create_staff(req, uow)

@router.post(
    "/get-verification", 
    response_model=StaffBeforeVerifyAuthResponse,
    summary="provide phone number and password and get verification token"
)
def get_verification(
    req: StaffSignInRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    return get_verification_token(req, uow)


@router.post(
    "/verify-auth", 
    response_model=AuthResponse,
    summary="Verify auth tokens and get access token"
)
def login(
    req: StaffVerifyOTPRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    return authenticate_staff(req, uow)


@router.get(
    "/me", 
    # response_model=StaffResponse,
    summary="Get your own staff profile"
)
def read_own_profile(
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return uow.staff.get(user["id"])


@router.post(
    "/change-password",
    response_model=AuthResponse,
    summary="Change your own password after OTP verification"
)
def change_password(
    req: ChangePasswordRequest,
    uow: UnitOfWork = Depends(get_uow),
    user = Depends(require_member),
):
    return change_own_password(req, uow, user)

@router.post(
    "/admin-change-password",
    response_model=AuthResponse,
    summary="Admin changes another staff member's password after OTP verification"
)
def change_password_admin(
    req: ChangePasswordRequest,
    user=Depends(require_superadmin),
    uow: UnitOfWork = Depends(get_uow),
):
    return change_staff_password(req, uow)