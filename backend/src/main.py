import uvicorn
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config
from core.redis import create_redis, close_redis
from core.rate_limiter import limiter as rate_limiter

from auth import router as auth_router
from auth.simple import router as simple_auth_router
from vehicles import router as vehicles_router
from stations import router as stations_router
from travels import router as travels_router
from tracking import router as tracking_router
from history import router as history_router
from reviews import router as reviews_router
from websocket import router as websocket_router

import firebase_admin
from firebase_admin import credentials

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# -- logging --

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.ERROR)

# -- init firebase (optional; simple auth works without it) --
try:
    firebase_admin.get_app()
except ValueError:
    try:
        cred = credentials.Certificate(config.FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        logging.warning("Firebase init skipped (simple auth does not require it): %s", e)

# -- init sub-apps --
api_v1 = FastAPI(
    title=f"{config.APP_TITLE} v1",
    version=config.APP_VERSION,
)

# -- routes --
api_v1.include_router(auth_router)
api_v1.include_router(simple_auth_router)
api_v1.include_router(vehicles_router)
api_v1.include_router(stations_router)
api_v1.include_router(travels_router)
api_v1.include_router(tracking_router)
api_v1.include_router(history_router)
api_v1.include_router(reviews_router)

# -- lifespan: Redis + Postgres listener --
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # -- redis --
    r = create_redis()
    app.state.redis = r
    api_v1.state.redis = r

    # WebSocket manager needs redis for pub/sub
    from services.websocket_manager import manager
    manager.set_redis(r)

    try:
        yield
    finally:
        # -- redis --
        close_redis(r)

# -- init app --
app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- mount apps --
app.mount(config.API_V1_PREFIX, api_v1)

# WebSocket routes (mounted on main app, not api_v1)
app.include_router(websocket_router)

# -- rate limiter --

def set_limiter(app: FastAPI) -> None:
    app.state.limiter = rate_limiter
    app.add_exception_handler(
        RateLimitExceeded, 
        _rate_limit_exceeded_handler
    )
    app.add_middleware(SlowAPIMiddleware)

set_limiter(app)
set_limiter(api_v1)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
