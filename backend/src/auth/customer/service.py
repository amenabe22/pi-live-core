from ..service import create_enduser, authenticate_enduser
from ..schemas import (
    AuthResponse,
    EndUserSignUpRequest,
    EndUserSignInRequest,
    EndUserResponse,
)

from core.uow import UnitOfWork 


def create_customer(
    data: EndUserSignUpRequest,
    uow: UnitOfWork
) -> AuthResponse:
    
    auth_res = create_enduser(data, uow)
    
    create_customer_if_not_exist(
        auth_res.user_id,
        uow
    )
    
    return auth_res


def authenticate_customer(
    data: EndUserSignInRequest,
    uow: UnitOfWork
) -> AuthResponse:

    auth_res = authenticate_enduser(data, uow)
    
    create_customer_if_not_exist(
        auth_res.user_id,
        uow
    )

    return auth_res


def create_customer_if_not_exist(
    profile_id: int,
    uow: UnitOfWork
):
    customer = uow.customer.get_by(profile_id=profile_id)
    if customer:
        return
    
    with uow:
        uow.customer.add(
            uow.customer.model(
                profile_id=profile_id
            )
        )
