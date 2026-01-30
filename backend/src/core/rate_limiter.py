from slowapi import Limiter
from slowapi.util import get_remote_address
from core.config import config


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    application_limits=["1000/minute"],
    headers_enabled=True,
    key_prefix="qrides",
    # storage_uri=config.REDIS_URL
)