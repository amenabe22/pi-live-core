from typing import Dict, Any
from sqlalchemy.orm import Session

from core.repository import BaseRepository
from common.models import Profile


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session: Session):
        super().__init__(session, Profile)