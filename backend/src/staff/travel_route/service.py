from fastapi import HTTPException, status

from core.uow import UnitOfWork
from core.types import Paginated
from common.schemas import TravelRouteResponse, TravelRouteCreate, TravelRouteUpdate


# TODO: check/validate if route passes through station

def _raise_if_missing_stations(
    station_ids: list[str], 
    uow: UnitOfWork
) -> None:

    if not station_ids:
        return

    missing = uow.travel_route.get_missing_station_ids(station_ids)
    
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Some station_ids do not exist; missing_station_ids: {missing}",
        )


def create_travel_route(
    data: TravelRouteCreate,
    created_by: str,
    uow: UnitOfWork,
) -> TravelRouteResponse:

    if uow.travel_route.get_by(name=data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Travel route with this name already exists",
        )

    _raise_if_missing_stations(data.station_ids, uow)

    with uow:
        route = uow.travel_route.add(
            uow.travel_route.model(
                name=data.name,
                polyline=dict(data.polyline),
                station_ids=data.station_ids,
                created_by=created_by,
            )
        )

    return TravelRouteResponse.from_orm(
        uow.travel_route.get(route.id)
    )


def update_travel_route(
    data: TravelRouteUpdate,
    route_id: str,
    uow: UnitOfWork,
) -> TravelRouteResponse:

    route = uow.travel_route.get(route_id)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel route not found",
        )

    if data.name and data.name != route.name:
        existing = uow.travel_route.get_by(name=data.name)
        if existing and existing.id != route_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Travel route with this name already exists",
            )

    patched_data = data.dict(exclude_unset=True)

    if "station_ids" in patched_data and patched_data["station_ids"] is not None:
        _raise_if_missing_stations(patched_data["station_ids"], uow)

    with uow:
        uow.travel_route.patch(
            obj=route,
            data=patched_data,
        )

    return TravelRouteResponse.from_orm(
        uow.travel_route.get(route.id)
    )


def get_travel_route(
    route_id: str,
    uow: UnitOfWork,
) -> TravelRouteResponse:

    route = uow.travel_route.get(route_id)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel route not found",
        )

    return TravelRouteResponse.from_orm(route)


def list_travel_routes(
    uow: UnitOfWork,
    *,
    skip: int = 0,
    limit: int = 100,
) -> Paginated[TravelRouteResponse]:

    items, total_items, total_pages = uow.travel_route.list(
        skip=skip,
        limit=limit,
    )

    return Paginated[TravelRouteResponse](
        items=items,
        total_items=total_items,
        total_pages=total_pages,
    )
