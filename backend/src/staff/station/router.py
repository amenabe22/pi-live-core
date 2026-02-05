from uuid import UUID
from fastapi import (
    APIRouter, Depends, Query, status
)

from core.dependencies import get_uow
from core.uow import UnitOfWork
from core.types import Paginated
from auth.dependencies import require_member

from common.schemas import StationCreate, StationUpdate, StationResponse
from .service import (
    create_station, update_station, 
    get_station, list_stations
)

router = APIRouter(prefix="/stations", tags=["stations-admin"])


@router.post(
    "",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a station",
)
def create_a_station(
    station: StationCreate,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow)
):
    return create_station(station, user["id"],  uow)


@router.patch(
    "/{station_id}",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a station",
)
def update_a_station(
    station_id: UUID,
    station: StationUpdate,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return update_station(station, str(station_id), uow)


@router.get(
    "",
    response_model=Paginated[StationResponse],
    status_code=status.HTTP_200_OK,
    summary="List stations",
)
def get_stations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):

    return list_stations(uow, skip=skip, limit=limit)


@router.get(
    "/{station_id}",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get station by id",
)
def get_a_station(
    station_id: UUID,
    user=Depends(require_member),
    uow: UnitOfWork = Depends(get_uow),
):
    return get_station(str(station_id), uow)


