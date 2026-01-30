from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from core.uow import UnitOfWork
from ..service import (
    firebase_verify_token, firebase_revoke_token,
    verify_password, get_password_hash, create_jwt, 
    decode_jwt, get_new_auth
)
from ..schemas import AuthResponse
from .schemas import (
    StaffSignUpRequest, StaffSignInRequest, StaffResponse,
    StaffBeforeVerifyAuthResponse, StaffVerifyOTPRequest,
    ChangePasswordRequest
)

from core.const import Gender, StaffRole, TokenType
from core.config import config


def create_staff(
    data: StaffSignUpRequest,
    uow: UnitOfWork
) -> AuthResponse:
    if uow.users.get_by(email=data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if uow.users.get_by(phone_no=data.phone_no):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )

    hashed = get_password_hash(data.password)

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    firebase_phone_no = firebase_user.get("phone_number")

    if firebase_phone_no != data.phone_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase: provided phone number does not match the one associated with the request."
        )

    with uow:
        user = uow.users.add(
            uow.users.model(
                email    = data.email,
                phone_no = data.phone_no,
                password = hashed,
                roles    = [data.role.value],
                is_otp_verified = True
            ),
            flush=True
        )

        staff = uow.staff.add(
            uow.staff.model(
                user_id   = user.id,
                full_name = data.full_name,
                gender    = data.gender.value,
                type      = data.type,
            )
        )

    firebase_revoke_token(
        firebase_user.get("uid")
    )

    token = get_new_auth(uow, user)

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type='bearer'
    )

def get_verification_token(
    data: StaffSignInRequest,
    uow: UnitOfWork
) -> StaffBeforeVerifyAuthResponse:
    
    user = uow.users.get_by(phone_no=data.phone_no)
    if not user or not verify_password(data.password, user.password or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credential"
        )

    if not uow.staff.get_by(user_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a staff member"
        )

    token_data = {
        "type": TokenType.INTERMEDIATE_TOKEN,
        "id": str(user.id),
        "phone_no": data.phone_no
    }

    return StaffBeforeVerifyAuthResponse(
        verification_token=create_jwt(token_data, minutes=config.INTERMEDIATE_TOKEN_EXPIRE_MINUTES)
    )

def authenticate_staff(
    data: StaffVerifyOTPRequest,
    uow: UnitOfWork
) -> AuthResponse:

    token_data = decode_jwt(data.verification_token)

    if not token_data.get("type") == TokenType.INTERMEDIATE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not valid verification token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    phone_no = token_data.get("phone_no")

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    firebase_phone_no = firebase_user.get("phone_number")

    if firebase_phone_no != phone_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase: provided phone number does not match the one associated with the request."
        )


    user = uow.users.get_by(phone_no=phone_no)
    token = get_new_auth(uow, user)

    firebase_revoke_token(
        firebase_user.get("uid")
    )

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type='bearer'
    )


def change_staff_password(
    data: ChangePasswordRequest,
    uow: UnitOfWork
) -> AuthResponse:

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    
    firebase_phone_no = firebase_user.get("phone_number")
    if not firebase_phone_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase user has no phone number"
        )

    user = uow.users.get_by(phone_no=firebase_phone_no)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    staff_record = uow.staff.get_by(user_id=user.id)
    if not staff_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a staff member"
        )

    with uow:
        updated_user = uow.users.patch(
            obj=user,
            data={"password": get_password_hash(data.new_password)}
        )

    token = get_new_auth(uow, updated_user)

    firebase_revoke_token(firebase_user.get("uid"))

    return AuthResponse(
        user_id=updated_user.id,
        access_token=token,
        token_type="bearer"
    )


def change_own_password(
    data: ChangePasswordRequest,
    uow: UnitOfWork,
    user: dict
) -> AuthResponse:

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    
    db_user = uow.users.get_by(id=user["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if firebase_user.get("phone_number") != db_user.phone_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase phone number does not match the current user"
        )

    if not uow.staff.get_by(user_id=db_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a staff member"
        )

    with uow:
        updated_user = uow.users.patch(
            obj=db_user,
            data={"password": get_password_hash(data.new_password)}
        )

    token = get_new_auth(uow, updated_user)
    firebase_revoke_token(firebase_user.get("uid"))

    return AuthResponse(
        user_id=updated_user.id,
        access_token=token,
        token_type="bearer"
    )
