from typing import Generator
from fastapi import Request

from core.db import SessionLocal
from core.uow import UnitOfWork


def get_uow(request: Request) -> Generator[UnitOfWork, None, None]:
    session = SessionLocal()
    uow = UnitOfWork(session, cache=request.app.state.redis)
    try:
        yield uow
    finally:
        session.close()
