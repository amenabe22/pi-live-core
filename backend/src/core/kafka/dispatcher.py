import logging
from typing import Callable, Dict
from confluent_kafka import Message
from .const import KafkaTopic
from .handlers import (
    handle_default
)

logger = logging.getLogger("kafka")

Handler = Callable[[Message], None]

topic_handlers: Dict[str, Handler] = {
    KafkaTopic.NA.value: handle_default,
}

default_handler: Handler = handle_default


def select_handler(msg: Message) -> Handler:
    t = msg.topic()
    if t in topic_handlers:
        return topic_handlers[t]
    return default_handler


def dispatch(msg: Message) -> bool:
    try:
        select_handler(msg)(msg)
        return True
    except Exception:
        logger.exception(
            "[dispatcher] error topic=%s partition=%d offset=%d",
            msg.topic(), msg.partition(), msg.offset()
        )
        return False