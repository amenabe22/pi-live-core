from typing import Generator
from fastapi import Request
import redis

from core.db import SessionLocal
from core.uow import UnitOfWork


def get_redis(request: Request) -> redis.Redis:
    """Get Redis client from app state (for api_v1 routes, use api_v1.state.redis)."""
    return request.app.state.redis


def get_uow(request: Request) -> Generator[UnitOfWork, None, None]:
    session = SessionLocal()
    uow = UnitOfWork(session, cache=request.app.state.redis)
    try:
        yield uow
    finally:
        session.close()
