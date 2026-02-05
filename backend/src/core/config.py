from pydantic_settings import BaseSettings
from pydantic import  AnyHttpUrl, RedisDsn
from typing import List, Literal, Tuple


class Config(BaseSettings):
    # App metadata
    APP_TITLE: str       = "pi-live-core-api"
    APP_DESCRIPTION: str = ""
    APP_VERSION: str     = "0.1.0"
    APP_ENC_KEY: str

    # API versioning
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl | Literal["*"]]

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

    # Kafka
    # KAFKA_BOOTSTRAP_SERVERS: str
    # KAFKA_SECURITY_PROTOCOL: str
    # KAFKA_SASL_MECHANISM: str
    # KAFKA_SASL_USERNAME: str
    # KAFKA_SASL_PASSWORD: str

    # Kafka tuning
    KAFKA_CLIENT_ID: str = "pi-live-consumers"
    KAFKA_GROUP_PREFIX: str = "pi-live"
    KAFKA_AUTO_OFFSET_RESET: Literal["earliest", "latest"] = "earliest"
    KAFKA_POLL_TIMEOUT_MS: int = 1000
    KAFKA_SESSION_TIMEOUT_MS: int = 45_000
    KAFKA_MAX_POLL_INTERVAL_MS: int = 300_000
    KAFKA_ALLOW_AUTO_CREATE_TOPICS: bool = False
    KAFKA_ISOLATION_LEVEL: Literal["read_uncommitted", "read_committed"] = "read_committed"

    # Kafka throughput tuning
    KAFKA_BATCH_SIZE: int = 1000
    KAFKA_MAX_WORKERS: int = 24
    KAFKA_WORK_QUEUE_MAXSIZE: int = 50_000
    KAFKA_COMMIT_BATCH_MSGS: int = 5000
    KAFKA_COMMIT_INTERVAL_SECS: float = 0.5
    KAFKA_PAUSE_FRACTION: float = 0.8
    KAFKA_RESUME_FRACTION: float = 0.3

    # Kafka Broker/buffer tuning
    KAFKA_FETCH_MIN_BYTES: int = 1_048_576   # 1 MiB
    KAFKA_FETCH_WAIT_MAX_MS: int = 50
    KAFKA_QUEUED_MAX_KB: int = 1_048_576     # 1 GiB
    KAFKA_QUEUED_MIN_MSGS: int = 10_000
    KAFKA_STATS_INTERVAL_MS: int = 0

    # Kafka misc tuning
    KAFKA_SHUTDOWN_DRAIN_SECS: float = 60.0

    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }

config = Config()
