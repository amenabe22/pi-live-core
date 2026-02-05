from sqlalchemy import String, Integer, column, values
from sqlalchemy.orm import Session

from core.repository import BaseRepository
from common.models import TravelRoute, Station


class TravelRouteRepository(BaseRepository[TravelRoute]):
    def __init__(self, session: Session):
        super().__init__(session, TravelRoute)

    def get_missing_station_ids(
        self, 
        station_ids: list[str]
    ) -> list[str]:
        """
        existence check for station_ids then returns station IDs that do NOT exist.
        """

        ids = list(
            dict.fromkeys(
                str(sid) for sid in (
                    station_ids or []
                ) 
                if sid is not None
            )
        )

        if not ids:
            return []

        input_ids = (
            values(
                column("sid", String(36)),
                column("ord", Integer),
                name="input_ids",
            )
            .data([(sid, i) for i, sid in enumerate(ids)])
            .alias("input_ids")
        )

        rows = (
            self.session.query(input_ids.c.sid)
            .select_from(input_ids)
            .outerjoin(Station, Station.id == input_ids.c.sid)
            .filter(Station.id.is_(None))
            .order_by(input_ids.c.ord)
            .all()
        )

        return [sid for (sid,) in rows]
