import re
import orjson
import logging
from confluent_kafka import Message

logger = logging.getLogger("kafka")


def handle_default(msg: Message) -> None:
    logger.warning(
        "[unhandled event] topic=%s partition=%d offset=%d",
        msg.topic(), msg.partition(), msg.offset()
    )
