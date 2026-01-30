from typing import Dict, Any
from sqlalchemy.orm import Session

from core.repository import BaseRepository
from common.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)