from uuid import UUID
from core.uow import UnitOfWork
from core.types import Paginated
from fastapi import HTTPException, status

from common.schemas import StationCreate, StationUpdate, StationResponse

def create_station(
    data: StationCreate,
    created_by: UUID, 
    uow: UnitOfWork
) -> StationResponse:

    if uow.station.get_by(name=data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Station with this name already exists"
        )

    with uow:
        station = uow.station.add(
            uow.station.model(
                name=data.name,
                address=data.address,
                latitude=data.latitude,
                longitude=data.longitude,
                created_by=created_by
            ),
            flush=True
        )

    return StationResponse.from_orm(station)

def update_station(
    data: StationUpdate,
    station_id: UUID,
    uow: UnitOfWork
) -> StationResponse:
    
    station = uow.station.get(station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )

    if data.name and data.name != station.name:
        existing = uow.station.get_by(name=data.name)
        if existing and existing.id != station_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Station with this name already exists"
            )

    with uow:
        station = uow.station.patch(
            obj=station,
            data=data.dict(exclude_unset=True, exclude_none=True)
        )

    return StationResponse.from_orm(station)

def get_station(
    station_id: UUID, 
    uow: UnitOfWork
) -> StationResponse:

    station = uow.station.get(station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    return StationResponse.from_orm(station)

def list_stations(
    uow: UnitOfWork, 
    *,
    skip: int = 0, 
    limit: int = 100
) -> Paginated[StationResponse]:

    items, total_items, total_pages = uow.station.list(
        skip=skip, 
        limit=limit
    )

    return Paginated[StationResponse](
        items=items, 
        total_items=total_items, 
        total_pages=total_pages
    )