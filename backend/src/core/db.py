from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

import re
import asyncpg
from core.config import config


# -- sync ORM --

engine: Engine = create_engine(
    config.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()
ViewBase = declarative_base()


# -- async ORM --

def to_async_url(url: str) -> str:

    url = re.sub(r"^postgres(?:ql)?(\+[^:]+)?://", "postgresql+asyncpg://", url)
    parts = urlsplit(url)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))

    q.pop("sslmode", None)
    q.pop("channel_binding", None)
    new_query = urlencode(q)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

async_engine = create_async_engine(
    to_async_url(config.DATABASE_URL),
    pool_pre_ping=True,
    future=True,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


# -- LISTEN connection (asyncpg) --

listen_conn: asyncpg.Connection | None = None

def to_asyncpg_dsn(dsn: str) -> str:

    dsn = re.sub(r"^postgres(?:ql)?(\+[^:]+)?://", "postgresql://", dsn)
    parts = urlsplit(dsn)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))

    q.pop("sslmode", None)
    q.pop("channel_binding", None)
    new_query = urlencode(q)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

async def open_listen_connection(dsn: str | None = None) -> asyncpg.Connection:
    global listen_conn
    
    if listen_conn is not None and not listen_conn.is_closed():
        return listen_conn
    
    pg_dsn = to_asyncpg_dsn(dsn or config.DATABASE_URL)
    listen_conn = await asyncpg.connect(pg_dsn)
    
    return listen_conn

async def close_listen_connection() -> None:
    global listen_conn
    
    if listen_conn is not None:
        try:
            await listen_conn.close()
        finally:
            listen_conn = None

async def ping_listen_connection() -> bool:
    
    if listen_conn is None or listen_conn.is_closed():
        return False
    
    try:
        await listen_conn.execute("SELECT 1")
        return True
    except Exception:
        return False
