from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from core.dependencies import get_uow
from core.uow import UnitOfWork
from core.types import Paginated
from auth.dependencies import require_member

from common.schemas import (
    TravelRouteCreate, TravelRouteUpdate, TravelRouteResponse
)
from .service import (
    create_travel_route, update_travel_route,
    get_travel_route, list_travel_routes
)

router = APIRouter(prefix="/travel-routes", tags=["travel-routes-admin"])


@router.post(
    "",
    response_model=TravelRouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a travel route",
)
def create_a_travel_route(
    route: TravelRouteCreate,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return create_travel_route(route, user["id"], uow)


@router.patch(
    "/{route_id}",
    response_model=TravelRouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a travel route",
)
def update_a_travel_route(
    route_id: UUID,
    route: TravelRouteUpdate,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return update_travel_route(route, str(route_id), uow)


@router.get(
    "",
    response_model=Paginated[TravelRouteResponse],
    status_code=status.HTTP_200_OK,
    summary="List travel routes",
)
def get_travel_routes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return list_travel_routes(uow, skip=skip, limit=limit)


@router.get(
    "/{route_id}",
    response_model=TravelRouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get travel route by id",
)
def get_a_travel_route(
    route_id: UUID,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return get_travel_route(str(route_id), uow)
