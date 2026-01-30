import uvicorn
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config
from core.redis import create_redis, close_redis
from core.rate_limiter import limiter as rate_limiter

from auth import router as auth_router

import firebase_admin
from firebase_admin import credentials

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# -- logging --

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.ERROR)

# -- init firebase --
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(config.FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)

# -- init sub-apps --
api_v1 = FastAPI(
    title=f"{config.APP_TITLE} v1",
    version=config.APP_VERSION,
)

# -- routes --
api_v1.include_router(auth_router)

# -- lifespan: Redis + Postgres listener --
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # -- redis --
    r = create_redis()
    app.state.redis = r
    api_v1.state.redis = r


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
