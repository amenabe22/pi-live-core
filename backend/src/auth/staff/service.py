from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from core.uow import UnitOfWork
from ..service import (
    firebase_verify_token, firebase_revoke_token,
    verify_password, get_password_hash, create_jwt,
    decode_jwt, get_new_auth, authenticate_with_google_staff
)
from ..schemas import AuthResponse, GoogleSignInRequest
from .schemas import (
    StaffSignUpRequest, StaffSignInRequest, StaffResponse,
    StaffBeforeVerifyAuthResponse, StaffVerifyOTPRequest,
    ChangePasswordRequest, BootstrapSuperAdminRequest
)

from core.const import Gender, Role, StaffRole, TokenType
from core.config import config


def create_first_superadmin(
    data: BootstrapSuperAdminRequest,
    uow: UnitOfWork
) -> AuthResponse:
    """Create the first super admin. Returns 403 if any staff already exist."""
    _, total, _ = uow.staff.list(limit=1)
    if total > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="First super admin already created. This endpoint is disabled."
        )

    hashed = get_password_hash(data.password) if data.password else None
    user = uow.users.get_by(email=data.email)

    if user:
        # Email already registered: add SUPERADMIN role and staff record; ensure profile
        with uow:
            roles = list(user.roles) if user.roles else []
            if Role.SUPERADMIN.value not in roles:
                roles.append(Role.SUPERADMIN.value)
            patch_data = {"roles": roles}
            if hashed is not None:
                patch_data["password"] = hashed
            uow.users.patch(user, patch_data, flush=True)
            if not uow.staff.get_by(user_id=user.id):
                uow.staff.add(
                    uow.staff.model(
                        user_id=user.id,
                        full_name=data.full_name,
                    )
                )
            profile = uow.profile.get(user.id)
            if not profile:
                uow.profile.add(
                    uow.profile.model(
                        user_id=user.id,
                        name=data.full_name,
                        gender=data.gender.value if data.gender else None,
                        dob=data.dob,
                    )
                )
            else:
                uow.profile.patch(
                    profile,
                    {
                        "name": data.full_name,
                        "gender": data.gender.value if data.gender else None,
                        "dob": data.dob,
                    },
                    flush=True,
                )
    else:
        with uow:
            user = uow.users.add(
                uow.users.model(
                    email=data.email,
                    phone_no=None,
                    password=hashed,
                    roles=[Role.SUPERADMIN],
                    is_otp_verified=True
                ),
                flush=True
            )
            uow.staff.add(
                uow.staff.model(
                    user_id=user.id,
                    full_name=data.full_name,
                )
            )
            uow.profile.add(
                uow.profile.model(
                    user_id=user.id,
                    name=data.full_name,
                    gender=data.gender.value if data.gender else None,
                    dob=data.dob,
                )
            )

    token = get_new_auth(uow, user)

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type="bearer"
    )


def create_staff(
    data: StaffSignUpRequest,
    uow: UnitOfWork
) -> AuthResponse:
    hashed = get_password_hash(data.password) if data.password else None

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    firebase_email = firebase_user.get("email")

    if not firebase_email or firebase_email != data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase: provided email does not match the one associated with the request."
        )

    user = uow.users.get_by(email=data.email)

    if user:
        # Email already registered (e.g. customer or other staff): add role and staff record
        with uow:
            roles = list(user.roles) if user.roles else []
            if data.role.value not in roles:
                roles.append(data.role.value)
            patch_data = {"roles": roles}
            if hashed is not None:
                patch_data["password"] = hashed
            uow.users.patch(user, patch_data, flush=True)
            existing_staff = uow.staff.get_by(user_id=user.id)
            if not existing_staff:
                uow.staff.add(
                    uow.staff.model(
                        user_id=user.id,
                        full_name=data.full_name,
                    )
                )
            # Ensure profile has name, gender, dob
            profile = uow.profile.get(user.id)
            if not profile:
                uow.profile.add(
                    uow.profile.model(
                        user_id=user.id,
                        name=data.full_name,
                        gender=data.gender.value,
                        dob=data.dob,
                    )
                )
            else:
                uow.profile.patch(
                    profile,
                    {
                        "name": data.full_name,
                        "gender": data.gender.value,
                        "dob": data.dob,
                    },
                    flush=True,
                )
    else:
        # New user: create user, staff, and profile (name, gender, dob)
        with uow:
            user = uow.users.add(
                uow.users.model(
                    email=data.email,
                    phone_no=None,
                    password=hashed,
                    roles=[data.role.value],
                    is_otp_verified=True
                ),
                flush=True
            )
            uow.staff.add(
                uow.staff.model(
                    user_id=user.id,
                    full_name=data.full_name,
                )
            )
            uow.profile.add(
                uow.profile.model(
                    user_id=user.id,
                    name=data.full_name,
                    gender=data.gender.value,
                    dob=data.dob,
                )
            )

    firebase_revoke_token(firebase_user.get("uid"))

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
    
    user = uow.users.get_by(email=data.email)
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
        "email": data.email
    }

    return StaffBeforeVerifyAuthResponse(
        verification_token=create_jwt(token_data, minutes=config.INTERMEDIATE_TOKEN_EXPIRE_MINUTES)
    )


def authenticate_staff_google(
    data: GoogleSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:
    return authenticate_with_google_staff(data, uow)

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

    email = token_data.get("email")

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    firebase_email = firebase_user.get("email")

    if not firebase_email or firebase_email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase: provided email does not match the one associated with the request."
        )

    user = uow.users.get_by(email=email)
    token = get_new_auth(uow, user)

    firebase_revoke_token(firebase_user.get("uid"))

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
    
    firebase_email = firebase_user.get("email")
    if not firebase_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase user has no email"
        )

    user = uow.users.get_by(email=firebase_email)
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

    if firebase_user.get("email") != db_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase email does not match the current user"
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
