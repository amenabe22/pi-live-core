from fastapi import APIRouter
from .station.router import router as station_router
from .travel_route.router import router as travel_route_router

router = APIRouter(prefix="/staff", tags=["staff"])

router.include_router(station_router)
router.include_router(travel_route_router)