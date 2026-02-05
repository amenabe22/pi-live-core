from typing import Dict, Any
from sqlalchemy.orm import Session

from core.repository import BaseRepository
from common.models import Station


class StationRepository(BaseRepository[Station]):
    def __init__(self, session: Session):
        super().__init__(session, Station)