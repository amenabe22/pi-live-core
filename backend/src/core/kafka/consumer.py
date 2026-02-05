import threading
import logging
import queue
import time
from typing import Dict, Tuple, List
from confluent_kafka import (
    Consumer, KafkaError, KafkaException, TopicPartition
)

from core.config import config
from .const import KafkaTopic
from .dispatcher import dispatch, topic_handlers

logger = logging.getLogger("kafka")

BATCH_SIZE = config.KAFKA_BATCH_SIZE
MAX_WORKERS = config.KAFKA_MAX_WORKERS
WORK_QUEUE_MAXSIZE = config.KAFKA_WORK_QUEUE_MAXSIZE
COMMIT_BATCH_MSGS = config.KAFKA_COMMIT_BATCH_MSGS
COMMIT_INTERVAL_SECS = config.KAFKA_COMMIT_INTERVAL_SECS
PAUSE_FRACTION = config.KAFKA_PAUSE_FRACTION
RESUME_FRACTION = config.KAFKA_RESUME_FRACTION
SHUTDOWN_DRAIN_SECS = config.KAFKA_SHUTDOWN_DRAIN_SECS

TOPIC_MAX_RETRIES: Dict[str, int] = {
    KafkaTopic.NA.value: 10,
}
DEFAULT_MAX_RETRIES = 5

TOPIC_RETRY_BACKOFF_SECS: Dict[str, float] = {
    KafkaTopic.NA.value: 0.5, # 500ms between retries
}
DEFAULT_RETRY_BACKOFF_SECS = 0.0

_consumers: Dict[str, Tuple[Consumer, threading.Thread, threading.Event]] = {}


def _base_consumer_conf(group_id: str) -> dict:
    return {
        "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
        "security.protocol": config.KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanisms": config.KAFKA_SASL_MECHANISM,
        "sasl.username": config.KAFKA_SASL_USERNAME,
        "sasl.password": config.KAFKA_SASL_PASSWORD,

        "group.id": group_id,
        "client.id": config.KAFKA_CLIENT_ID,

        "enable.auto.commit": False,
        "enable.auto.offset.store": False,

        "auto.offset.reset": config.KAFKA_AUTO_OFFSET_RESET,

        "session.timeout.ms": int(config.KAFKA_SESSION_TIMEOUT_MS),
        "max.poll.interval.ms": int(config.KAFKA_MAX_POLL_INTERVAL_MS),

        "isolation.level": config.KAFKA_ISOLATION_LEVEL,
        "allow.auto.create.topics": bool(config.KAFKA_ALLOW_AUTO_CREATE_TOPICS),

        "partition.assignment.strategy": "cooperative-sticky",

        "fetch.min.bytes": int(config.KAFKA_FETCH_MIN_BYTES),
        "fetch.wait.max.ms": int(config.KAFKA_FETCH_WAIT_MAX_MS),
        "queued.max.messages.kbytes": int(config.KAFKA_QUEUED_MAX_KB),
        "queued.min.messages": int(config.KAFKA_QUEUED_MIN_MSGS),
        "statistics.interval.ms": int(config.KAFKA_STATS_INTERVAL_MS),
    }

def build_consumer(group_id: str) -> Consumer:
    conf = _base_consumer_conf(group_id)
    return Consumer(conf)

def _handle_message(msg) -> bool:
    return dispatch(msg)

def _poll_loop(
    topic: str,
    consumer: Consumer, 
    stop_event: threading.Event
) -> None:

    poll_timeout_sec = max(0.01, float(config.KAFKA_POLL_TIMEOUT_MS) / 1000.0)

    work_q = queue.Queue(maxsize=WORK_QUEUE_MAXSIZE)
    ack_q = queue.Queue()

    max_acked: Dict[Tuple[str, int], int] = {}
    paused = False
    assigned_partitions = []

    failure_counts: Dict[Tuple[str, int, int], int] = {}
    failure_counts_lock = threading.Lock()

    def _should_ack_message(msg, handler_ok: bool) -> bool:
        topic_name = msg.topic()
        partition = msg.partition()
        offset = msg.offset()
        key = (topic_name, partition, offset)

        if handler_ok:
            with failure_counts_lock:
                failure_counts.pop(key, None)
            return True

        max_retries = TOPIC_MAX_RETRIES.get(topic_name, DEFAULT_MAX_RETRIES)

        if max_retries <= 0:
            return True

        with failure_counts_lock:
            failures = failure_counts.get(key, 0) + 1
            failure_counts[key] = failures

        if failures >= max_retries:
            logger.error(
                "kafka-handler-max-retries-exceeded topic=%s partition=%d offset=%d failures=%d max_retries=%d",
                topic_name,
                partition,
                offset,
                failures,
                max_retries,
            )
            with failure_counts_lock:
                failure_counts.pop(key, None)
            return True

        logger.warning(
            "kafka-handler-failed-will-retry topic=%s partition=%d offset=%d failures=%d max_retries=%d",
            topic_name,
            partition,
            offset,
            failures,
            max_retries,
        )
        return False

    def _worker():
        while True:
            try:
                msg = work_q.get(timeout=0.1)
            except queue.Empty:
                if stop_event.is_set():
                    break
                continue
    
            try:
                if msg is None:
                    break

                topic_name = msg.topic()
                backoff_secs = TOPIC_RETRY_BACKOFF_SECS.get(
                    topic_name,
                    DEFAULT_RETRY_BACKOFF_SECS,
                )

                # retry loop for a single message
                while True:
                    ok = _handle_message(msg)
                    if _should_ack_message(msg, ok):
                        ack_q.put(
                            (
                                msg.topic(),
                                msg.partition(),
                                msg.offset()
                            )
                        )
                        break

                    if stop_event.is_set():
                        break

                    if backoff_secs > 0:
                        time.sleep(backoff_secs)
    
            finally:
                work_q.task_done()

    workers = []
    for i in range(MAX_WORKERS):
        
        t = threading.Thread(
            target=_worker, 
            name=f"kafka-consumer-worker-{topic}-{i}", 
            daemon=True
        )
        t.start()
        
        workers.append(t)

    def _on_assign(c: Consumer, parts):
        nonlocal assigned_partitions

        c.incremental_assign(parts)
        assigned_partitions = list({
            (tp.topic, tp.partition): tp for tp in (assigned_partitions + parts)
        }.values())

        logger.info(
            "partition-assigned topic=%s partitions=%s",
            topic, [tp.partition for tp in parts]
        )

    def _on_revoke(c: Consumer, parts):
        nonlocal assigned_partitions

        _drain_acks_and_maybe_commit(force_sync=True)
        c.incremental_unassign(parts) # Self-Note: cooperative-sticky requires incremental unassign
        assigned_partitions = [
            tp for tp in assigned_partitions if tp not in parts
        ]

        logger.info(
            "partition-revoked topic=%s partitions=%s",
            topic, [tp.partition for tp in parts]
        )

    consumer.subscribe(
        [topic], 
        on_assign=_on_assign, 
        on_revoke=_on_revoke
    )

    logger.info("consumer-subscribed topic=%s poll_timeout_s=%.3f", topic, poll_timeout_sec)

    last_commit_ts = time.monotonic()
    ack_since_commit = 0

    def _pause_if_needed():
        nonlocal paused

        if not paused and work_q.qsize() >= int(WORK_QUEUE_MAXSIZE * PAUSE_FRACTION):
            try:
                consumer.pause(assigned_partitions)
            except Exception:
                pass
            paused = True

    def _resume_if_needed():
        nonlocal paused

        if paused and work_q.qsize() <= int(WORK_QUEUE_MAXSIZE * RESUME_FRACTION):
            try:
                consumer.resume(assigned_partitions)
            except Exception:
                pass
            paused = False

    def _drain_acks():
        nonlocal ack_since_commit

        drained = 0
        while True:
            
            try:
                tp, p, off = ack_q.get_nowait()
            except queue.Empty:
                break
            
            key = (tp, p)
            prev = max_acked.get(key)
            
            if prev is None or off > prev:
                max_acked[key] = off
            
            ack_q.task_done()
            drained += 1
        
        ack_since_commit += drained
        return drained

    def _commit_offsets(async_commit: bool):
        
        if not max_acked:
            return
        
        tps = [
            TopicPartition(t, p, o + 1) for (t, p), o in max_acked.items()
        ]
        
        try:
            consumer.commit(offsets=tps, asynchronous=async_commit)
        except KafkaException:
            pass

    def _drain_acks_and_maybe_commit(force_sync: bool = False):
        nonlocal last_commit_ts, ack_since_commit
        
        _drain_acks()
        now = time.monotonic()
        
        if (
            force_sync or ack_since_commit >= COMMIT_BATCH_MSGS 
            or (now - last_commit_ts) >= COMMIT_INTERVAL_SECS
        ):
            
            _commit_offsets(
                async_commit=not force_sync
            )
            last_commit_ts = now
            ack_since_commit = 0

    try:
        while not stop_event.is_set():
            
            _pause_if_needed()
            
            msgs = consumer.consume(
                num_messages=BATCH_SIZE, 
                timeout=poll_timeout_sec
            )
            
            if msgs:
                for msg in msgs:
                    if msg is None:
                        continue
            
                    if msg.error():
                        err = msg.error()
                        if err.code() == KafkaError._PARTITION_EOF:
                            continue
                        if err.fatal():
                            raise KafkaException(err)
                        continue
            
                    try:
                        work_q.put_nowait(msg)
                    except queue.Full:
                        time.sleep(0.001) # small backoff... partition pause already engaged

            _resume_if_needed()
            _drain_acks_and_maybe_commit(force_sync=False)

    finally:
        try:
            try:
                consumer.pause(assigned_partitions)
            except Exception:
                pass
            consumer.wakeup()
        except Exception:
            pass

        deadline = time.monotonic() + float(SHUTDOWN_DRAIN_SECS)
        while (
            time.monotonic() < deadline and
            (not work_q.empty() or not ack_q.empty())
        ):
            _drain_acks_and_maybe_commit(force_sync=False)
            time.sleep(0.01)

        _drain_acks_and_maybe_commit(force_sync=True)

        for _ in workers:
            work_q.put_nowait(None)
       
        for t in workers:
            t.join(timeout=1.0)

        try:
            consumer.close()
        except Exception:
            pass


def _group_id_for(topic: str) -> str:
    return f"{config.KAFKA_GROUP_PREFIX}.{topic}"

def start_consumer_worker(
    *, 
    topic: str, 
    group_id: str | None = None
) -> None:

    if topic in _consumers:
        stop_consumer_worker(topic)

    gid = group_id or _group_id_for(topic)
    consumer = build_consumer(gid)
    stop_event = threading.Event()

    thread = threading.Thread(
        target=_poll_loop,
        args=(topic, consumer, stop_event),
        name=f"kafka-consumer-{topic}",
        daemon=True
    )
    thread.start()

    logger.info(
        "consumer-started topic=%s group_id=%s workers=%d batch_size=%d",
        topic, gid, MAX_WORKERS, BATCH_SIZE
    )

    _consumers[topic] = (consumer, thread, stop_event)

def stop_consumer_worker(topic: str) -> None:
    entry = _consumers.pop(topic, None)
    
    if not entry:
        return
    
    consumer, thread, stop_event = entry
    stop_event.set()
    
    try:
        consumer.wakeup()
    except Exception:
        pass
    
    thread.join(timeout=5.0)
    
    try:
        consumer.close()
    except Exception:
        pass

def start_consumers_for_topics(topics: List[str]) -> None:
    for t in topics:
        start_consumer_worker(topic=t)

def stop_all_consumers() -> None:
    for topic in list(_consumers.keys()):
        stop_consumer_worker(topic)


def start_consumers() -> None:
    start_consumers_for_topics(topic_handlers.keys())
