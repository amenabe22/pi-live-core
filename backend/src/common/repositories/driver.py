from typing import List, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from core.repository import BaseRepository
from common.models import Driver


class DriverRepository(BaseRepository[Driver]):
    def __init__(self, session: Session):
        super().__init__(session, Driver)
