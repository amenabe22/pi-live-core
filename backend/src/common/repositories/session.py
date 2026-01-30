from datetime import datetime
from typing import Dict, Any
from redis import Redis
from sqlalchemy.orm import Session as SQLAlchemySession

from core.repository import BaseRepository
from common.models import Session as SessionModel 


# fixme: session updates cache before commit
class SessionRepository(BaseRepository[SessionModel]):
    def __init__(self, sql_session: SQLAlchemySession, cache: Redis):
        super().__init__(sql_session, SessionModel, cache)
        self.cache_ttl = 180

    def create(self, user_id: int, expires_at: datetime) -> SessionModel:
        sess = self.model(
            user_id=user_id, 
            expires_at=expires_at
        )
        self.add(sess)
        self.session.flush()
        return sess

    def is_active(self, session_id: str) -> bool:

        cached = self._cache_get_bool(session_id)
        if cached != None:
            return cached

        now = datetime.utcnow()
        rec = (
            self.session.query(self.model)
            .filter(
                self.model.id == session_id,
                self.model.revoked == False,
                self.model.expires_at > now,
            )
            .first()
        )
        active = rec is not None

        self._cache_set_bool(session_id, active)
        return active


    def revoke(self, session_id: str) -> bool:

        rec = self.get(session_id)
        if not rec:
            return False

        rec.revoked = True
        rec.revoked_at = datetime.utcnow()

        self._cache_del(session_id)
        return True
    
    def revoke_all(self, user_id: int) -> int:

        ids = [
            sid
            for (sid,) in self.session.query(self.model.id)
            .filter(
                self.model.user_id == user_id,
                self.model.revoked == False
            )
            .all()
        ]

        now = datetime.utcnow()
        count = (
            self.session
            .query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.revoked == False
            )
            .update(
                {"revoked": True, "revoked_at": now},
                synchronize_session="fetch"
            )
        )

        if ids: self._cache_del(*ids)
        return count

    # -- cache helpers --
    def _active_key(self, session_id: str) -> str:
        return f"sess:{session_id}:active"

    def _cache_get_bool(self, session_id: str) -> bool | None:
        val = self.cache.get(self._active_key(session_id))
        
        if val is None:
            return None
        
        return val == "1"

    def _cache_set_bool(self, session_id: str, value: bool) -> None:
        self.cache.setex(
            self._active_key(session_id),
            self.cache_ttl,
            "1" if value else "0"
        )

    def _cache_del(self, *session_ids: str) -> None:
        if session_ids:
            keys = [self._active_key(sid) for sid in session_ids]
            self.cache.delete(*keys)