import redis
from core.config import config


def create_redis() -> redis.Redis:
    return redis.from_url(
        config.REDIS_URL,
        decode_responses=True,
        health_check_interval=30,
        socket_timeout=5,
        retry_on_timeout=True,
    )

def close_redis(r: redis.Redis) -> None:
    r.close()