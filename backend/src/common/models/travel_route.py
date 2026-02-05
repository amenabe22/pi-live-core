import json
import uuid
from sqlalchemy import (
    Column, ForeignKey, String, DateTime, func, text, cast, select
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import object_session
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement, WKTElement
from core.db import Base


class TravelRoute(Base):
    __tablename__ = "travel_route"

    id: str = Column(
        String(length=36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    name: str = Column(
        String(length=255),
        nullable=False,
        index=True,
    )

    _polyline: WKBElement = Column(
        "polyline",
        Geometry(
            geometry_type="LINESTRING",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    )

    station_ids: list[str] = Column(
        ARRAY(String(length=36)),
        nullable=False,
        server_default=text("'{}'::varchar[]"),
    )

    created_by: str | None = Column(
        String(length=36),
        ForeignKey("staff.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: DateTime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: DateTime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @hybrid_property
    def polyline(self) -> dict | None:
        if self._polyline is None:
            return None

        sess = object_session(self)
        if sess is None or self.id is None:
            return None

        geojson_str = sess.scalar(
            select(
                func.ST_AsGeoJSON(type(self)._polyline)
            ).where(
                type(self).id == self.id
            )
        )
        return json.loads(geojson_str) if geojson_str else None

    @polyline.setter
    def polyline(self, value: dict | WKBElement | WKTElement | None) -> None:
        if value is None or isinstance(value, (WKBElement, WKTElement)):
            self._polyline = value
            return

        if isinstance(value, dict):
            self._polyline = func.ST_SetSRID(
                func.ST_GeomFromGeoJSON(json.dumps(value)),
                4326,
            )
            return

        raise TypeError(
            f"polyline expects GeoJSON (dict), WKB/WKTElement, or None. not {type(value)}"
        )

    @polyline.expression
    def polyline(cls):
        return cast(func.ST_AsGeoJSON(cls._polyline), JSONB)
