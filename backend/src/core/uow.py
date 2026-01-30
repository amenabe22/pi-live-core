from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from redis import Redis

from common.repositories import (
    UserRepository,
    SessionRepository, 
    ProfileRepository,
    StaffRepository,
    CustomerRepository,
    DriverRepository,
)


class UnitOfWork(AbstractContextManager):
    def __init__(self, session: Session, cache: Redis | None = None):
        self.session = session
        self.cache = cache

        # -- repositories --
        self.users = UserRepository(session)
        self.user_sessions = SessionRepository(session, cache)
        self.staff = StaffRepository(session)
        self.profile = ProfileRepository(session)
        self.driver = DriverRepository(session)
        self.customer = CustomerRepository(session)

    def __enter__(self) -> "UnitOfWork":
        if self.session.in_transaction():
            self._tx = self.session.begin_nested()
        else:
            self._tx = self.session.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type:
            self.session.rollback()
        else:
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
        self.session.close()
