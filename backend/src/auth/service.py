from fastapi import HTTPException, status, UploadFile

from firebase_admin import auth as firebase_auth
from datetime import datetime, timedelta
from passlib.context import CryptContext

import jwt

from core.config import config
from core.uow import UnitOfWork
from core.const import Gender, Role, TokenType, ETH_COUNTRY_CODE
from core.utils import country_code
from common.models import User as UserModel

from .schemas import (
    AuthResponse,
    EndUserSignUpRequest,
    EndUserSignInRequest,
    EndUserResponse,
    EndUserPhoneNoUpdate,
    GoogleSignInRequest,
)


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def firebase_verify_token(token: str) -> any:
    try:
        return firebase_auth.verify_id_token(
            token, check_revoked=True
        )
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Firebase: token has been revoked"
        )
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Firebase: invalid ID token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Firebase: authentication failed — {e}",
        )

def firebase_revoke_token(uid: str):
    try:
        firebase_auth.revoke_refresh_tokens(uid)
    except Exception as e:
        pass

def get_new_auth(uow: UnitOfWork, user: UserModel) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    with uow:
        uow.user_sessions.revoke_all(user.id)

        session = uow.user_sessions.create(
            user_id=user.id,
            expires_at=expire
        )

    token_data = {
        "type": TokenType.ACCESS_TOKEN,
        "id": str(user.id),
        "sid": session.id,
        "roles": user.roles
    }

    jwt_token = create_jwt(token_data, minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return jwt_token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_jwt(payload: dict, minutes: int) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=minutes)
    
    to_encode = {
        "data": payload, 
        "iat": now, 
        "exp": expire
    }

    return jwt.encode(
        to_encode, 
        config.JWT_SECRET_KEY, 
        algorithm=config.JWT_ALGORITHM
    )

def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, 
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        return payload.get("data", {})
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unkonw token error",
            headers={"WWW-Authenticate": "Bearer"}
        )

def validate_country_code(
    phone_no: str,
    uow: UnitOfWork
) -> bool:

    code = country_code(phone_no)
    if ETH_COUNTRY_CODE != code: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This phone number region is not eligible."
        )

def create_enduser(
    data: EndUserSignUpRequest,
    uow: UnitOfWork
) -> AuthResponse:

    hashed = get_password_hash(data.password) if data.password else None

    if data.phone_no is not None:
        validate_country_code(data.phone_no, uow)
        if uow.users.get_by(phone_no=data.phone_no):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered"
            )
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
                    phone_no=data.phone_no,
                    password=hashed,
                    roles=[Role.ENDUSER],
                ),
                flush=True
            )
            profile = uow.profile.add(
                uow.profile.model(
                    user_id=user.id,
                    name=data.name,
                    gender=data.gender.value,
                    dob=data.dob,
                )
            )
        firebase_revoke_token(firebase_user.get("uid"))
    else:
        if uow.users.get_by(email=data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        with uow:
            user = uow.users.add(
                uow.users.model(
                    email=data.email,
                    phone_no=None,
                    password=hashed,
                    roles=[Role.ENDUSER],
                ),
                flush=True
            )
            profile = uow.profile.add(
                uow.profile.model(
                    user_id=user.id,
                    name=data.name,
                    gender=data.gender.value,
                    dob=data.dob,
                )
            )

    token = get_new_auth(uow, user)

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type='bearer'
    )

def authenticate_enduser(
    data: EndUserSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:
    
    firebase_user = firebase_verify_token(data.firebase_auth_token)
    firebase_phone_no = firebase_user.get("phone_number")

    user = uow.users.get_by(phone_no=firebase_phone_no)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found please sign up first"
        )        

    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot login this account is suspended"
        )   

    token = get_new_auth(uow, user)

    firebase_revoke_token(
        firebase_user.get("uid")
    )

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type='bearer'
    )


def authenticate_with_google(
    data: GoogleSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:

    firebase_user = firebase_verify_token(data.firebase_id_token)
    email = firebase_user.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email"
        )

    user = uow.users.get_by(email=email)
    if not user:
        with uow:
            user = uow.users.add(
                uow.users.model(
                    email=email,
                    password=None,
                    roles=[Role.ENDUSER],
                ),
                flush=True
            )
            uow.profile.add(
                uow.profile.model(
                    user_id=user.id,
                    name=firebase_user.get("name"),
                    profile_picture=firebase_user.get("picture"),
                )
            )
    if Role.ENDUSER not in user.roles:
        with uow:
            uow.users.patch(
                user,
                {"roles": user.roles + [Role.ENDUSER]},
                flush=True
            )


    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot login this account is suspended"
        )

    token = get_new_auth(uow, user)
    firebase_revoke_token(firebase_user.get("uid"))

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type='bearer'
    )


def authenticate_with_google_staff(
    data: GoogleSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:

    firebase_user = firebase_verify_token(data.firebase_id_token)
    email = firebase_user.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email"
        )

    user = uow.users.get_by(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Sign up as staff first."
        )

    if not uow.staff.get_by(user_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a staff member"
        )

    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot login this account is suspended"
        )

    token = get_new_auth(uow, user)
    firebase_revoke_token(firebase_user.get("uid"))

    return AuthResponse(
        user_id=user.id,
        access_token=token,
        token_type='bearer'
    )


def update_phone_number_enduser(
    data: EndUserPhoneNoUpdate,
    user_id: int,
    uow: UnitOfWork
) -> EndUserResponse:

    firebase_user = firebase_verify_token(data.firebase_auth_token)
    firebase_phone_no = firebase_user.get("phone_number")

    validate_country_code(firebase_phone_no, uow)

    if uow.users.get_by(phone_no=firebase_phone_no):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )

    user = uow.users.get(user_id)

    if country_code(firebase_phone_no) != country_code(user.phone_no):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number cannot be changed to different region."
        )

    with uow:
        user.phone_no = firebase_phone_no

    firebase_revoke_token(
        firebase_user.get("uid")
    )

    profile = uow.profile.get(user_id)

    return EndUserResponse(
        user_id=profile.user_id,
        name=profile.name,
        gender=profile.gender,
        phone_no=user.phone_no,
        dob=profile.dob,
        profile_picture=profile.profile_picture,
    )
