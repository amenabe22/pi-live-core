from typing import Annotated, Generic, TypeVar, List, Literal
from pydantic import BaseModel, Field, model_validator

T = TypeVar('T')

PhoneNumber = Annotated[
    str,
    Field(
        ...,
        pattern=r'^\+[1-9]\d{1,14}$',
        min_length=2,
        max_length=16,
        strip_whitespace=True,
        description="Phone number in E.164 format (e.g. +14155552671)",
    ),
]

PhoneCountryCode = Annotated[
    str,
    Field(
        ...,
        pattern=r'^\+[1-9]\d{0,5}$',
        min_length=1,
        max_length=4,
        strip_whitespace=True,
        description="Country code (e.g. +141)",
    ),
]

ZipCode = Annotated[
    str,
    Field(
        ...,
        pattern=r'^[A-Za-z0-9\s\-]{3,10}$',
        min_length=3,
        max_length=10,
        strip_whitespace=True,
        description="Zip or postal code, 3 to 10 alphanumeric characters, spaces or hyphens allowed",
    ),
]

Latitude = Annotated[
    float,
    Field(
        ge=-90,
        le=90,
        description="Latitude in decimal degrees [-90, 90] (WGS84).",
    ),
]

Longitude = Annotated[
    float,
    Field(
        ge=-180,
        le=180,
        description="Longitude in decimal degrees [-180, 180] (WGS84).",
    ),
]

class Paginated(BaseModel, Generic[T]):
    items: List[T]
    total_items: int
    total_pages: int

    model_config = {
        "arbitrary_types_allowed": True
    }


# -- RFC 7946 GeoJSON Polygon | single polygon --

PolyPosition = tuple[float, float] #[lon, lat]
PolyLinearRing = Annotated[list[PolyPosition], Field(min_length=4)]
PolygonCoordinates = Annotated[list[PolyLinearRing], Field(min_length=1)]

class PolygonGeoJSON(BaseModel):
    type: Literal["Polygon"]
    coordinates: PolygonCoordinates

    @model_validator(mode="after")
    def validate_closed_rings(self):
        # Ensure each ring is closed (first == last). Auto-close if not.
        closed: list[PolyLinearRing] = []
        for ring in self.coordinates:
            if ring[0] != ring[-1]:
                ring = [*ring, ring[0]]
            closed.append(ring)
        self.coordinates = closed  # assign normalized rings
        return self