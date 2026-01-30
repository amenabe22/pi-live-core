import json
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, RedisDsn, field_validator
from typing import List, Literal, Union


class Config(BaseSettings):
    # App metadata
    APP_TITLE: str       = "pi-live-core-api"
    APP_DESCRIPTION: str = ""
    APP_VERSION: str     = "0.1.0"
    APP_ENC_KEY: str

    # API versioning
    API_V1_PREFIX: str = "/api/v1"

    # CORS (accepts JSON list, comma-separated string, or "*")
    BACKEND_CORS_ORIGINS: Union[List[Union[AnyHttpUrl, Literal["*"]]], str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["*"]

    # DB
    DATABASE_URL: str

    # JWT / Tokens
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    INTERMEDIATE_TOKEN_EXPIRE_MINUTES: int = 15

    FIREBASE_KEY_PATH: str = "firebase-key-secret.json"

    # Redis
    REDIS_URL: str

    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }

config = Config()
