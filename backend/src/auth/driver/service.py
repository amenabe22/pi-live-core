from fastapi import HTTPException, status

from ..service import create_enduser, authenticate_enduser, authenticate_with_google, get_password_hash
from ..schemas import (
    AuthResponse,
    EndUserSignUpRequest,
    EndUserSignInRequest,
    EndUserResponse,
    GoogleSignInRequest,
    CreateDriverRequest,
    CreateDriverResponse,
)

from core.uow import UnitOfWork
from core.const import Role


def create_driver_by_email(
    data: CreateDriverRequest,
    uow: UnitOfWork
) -> CreateDriverResponse:
    hashed = get_password_hash(data.password) if data.password else None
    user = uow.users.get_by(email=data.email)

    if user:
        if hashed is not None:
            with uow:
                uow.users.patch(user, {"password": hashed}, flush=True)
        profile = uow.profile.get(user.id)
        if not profile:
            with uow:
                uow.profile.add(
                    uow.profile.model(
                        user_id=user.id,
                        name=data.name,
                        gender=data.gender.value if data.gender else None,
                        dob=data.dob,
                    )
                )
        create_driver_if_not_exist(user.id, uow)
        return CreateDriverResponse(user_id=user.id, email=data.email)
    else:
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
            uow.profile.add(
                uow.profile.model(
                    user_id=user.id,
                    name=data.name,
                    gender=data.gender.value if data.gender else None,
                    dob=data.dob,
                )
            )
            create_driver_if_not_exist(user.id, uow)
        return CreateDriverResponse(user_id=user.id, email=data.email)


def authenticate_driver_google(
    data: GoogleSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:
    auth_res = authenticate_with_google(data, uow)
    if not uow.driver.get_by(profile_id=auth_res.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver. Only staff can create drivers."
        )
    return auth_res


def create_driver(
    data: EndUserSignUpRequest,
    uow: UnitOfWork
) -> AuthResponse:
    
    auth_res = create_enduser(data, uow)
    
    create_driver_if_not_exist(
        auth_res.user_id,
        uow
    )
    
    return auth_res


def authenticate_driver(
    data: EndUserSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:
    auth_res = authenticate_enduser(data, uow)
    if not uow.driver.get_by(profile_id=auth_res.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver. Only staff can create drivers."
        )
    return auth_res


def create_driver_if_not_exist(
    profile_id: str,
    uow: UnitOfWork
) -> None:
    driver = uow.driver.get_by(profile_id=profile_id)
    if driver:
        return
    with uow:
        uow.driver.add(
            uow.driver.model(
                profile_id=profile_id
            )
        )
