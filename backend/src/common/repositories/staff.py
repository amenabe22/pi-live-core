from typing import Dict, Any
from sqlalchemy.orm import Session

from core.repository import BaseRepository
from common.models import Staff


class StaffRepository(BaseRepository[Staff]):
    def __init__(self, session: Session):
        super().__init__(session, Staff)
