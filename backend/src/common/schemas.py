from uuid import UUID
from datetime import date, time, datetime, timezone
from decimal import Decimal

from typing import List, Optional

from pydantic import (
    BaseModel, AliasChoices, Field, ConfigDict, 
    condecimal, field_validator, computed_field, model_validator
)

from core.types import (
    Latitude, Longitude, PhoneCountryCode, ZipCode,
    PolygonGeoJSON, PolylineGeoJSON
)


# -- station schema --

class StationBase(BaseModel):
    name: str
    address: str
    latitude: Latitude
    longitude: Longitude


class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None

class StationResponse(StationBase):
    id: UUID

    class Config:
        from_attributes = True


# -- travel route schema --

class TravelRouteBase(BaseModel):
    name: str
    polyline: PolylineGeoJSON
    station_ids: list[UUID] = Field(default_factory=list)

class TravelRouteCreate(TravelRouteBase):
    pass

class TravelRouteUpdate(BaseModel):
    name: str | None = None
    polyline: PolylineGeoJSON | None = None
    station_ids: list[UUID] | None = None

class TravelRouteResponse(TravelRouteBase):
    id: UUID

    class Config:
        from_attributes = True
