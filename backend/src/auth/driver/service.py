from ..service import create_enduser, authenticate_enduser
from ..schemas import (
    AuthResponse,
    EndUserSignUpRequest,
    EndUserSignInRequest,
    EndUserResponse,
)

from core.uow import UnitOfWork 


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
    
    create_driver_if_not_exist(
        auth_res.user_id,
        uow
    )

    return auth_res


def create_driver_if_not_exist(
    profile_id: int,
    uow: UnitOfWork
):
    driver = uow.driver.get_by(profile_id=profile_id)
    if driver:
        return
    
    with uow:
        uow.driver.add(
            uow.driver.model(
                profile_id=profile_id
            )
        )
