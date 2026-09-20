import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from uuid import UUID

import redis.asyncio as redis

from apps.api.app.config import get_settings
from apps.api.app.contracts import Job

logger = logging.getLogger("nexora.worker")


JobHandlerFn = Callable[[Job], Awaitable[None]]


class RedisJobQueue:
    queue_key = "nexora:jobs"

    def __init__(self, client):
        self.client = client

    async def enqueue(self, job: Job) -> None:
        await self.client.rpush(self.queue_key, json.dumps(asdict(job), default=str))

    async def dequeue(self, timeout: int = 5) -> Job | None:
        item = await self.client.blpop(self.queue_key, timeout=timeout)
        if not item:
            return None
        _, raw = item
        payload = json.loads(raw)
        return Job(
            id=UUID(payload["id"]),
            type=payload["type"],
            payload=payload["payload"],
            priority=payload.get("priority", 0),
            attempt=payload.get("attempt", 0),
            metadata=payload.get("metadata"),
        )


class WorkerRuntime:
    def __init__(self, handlers: dict[str, JobHandlerFn] | None = None):
        settings = get_settings()
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        self.queue = RedisJobQueue(self.redis)
        self.handlers = handlers or {}
        self.stop_event = asyncio.Event()

    async def run(self):
        logger.info("worker starting")
        try:
            await self.redis.ping()
            logger.info("redis connection ready")
            while not self.stop_event.is_set():
                job = await self.queue.dequeue(timeout=2)
                if job is None:
                    continue
                handler = self.handlers.get(job.type)
                if handler is None:
                    logger.error("no handler registered", extra={"job_type": job.type, "job_id": str(job.id)})
                    continue
                try:
                    await handler(job)
                except Exception:
                    logger.exception("job failed", extra={"job_id": str(job.id), "job_type": job.type})
        finally:
            await self.redis.aclose()
            logger.info("worker stopped")

    def stop(self):
        self.stop_event.set()
