import asyncio,logging
import redis.asyncio as redis
from apps.api.app.config import get_settings
logger=logging.getLogger("nexora.worker")
class WorkerRuntime:
    def __init__(self):
        s=get_settings(); self.redis=redis.from_url(s.redis_url,decode_responses=True); self.stop_event=asyncio.Event()
    async def run(self):
        logger.info("worker starting")
        try: await self.redis.ping(); logger.info("redis connection ready"); await self.stop_event.wait()
        finally: await self.redis.aclose(); logger.info("worker stopped")
    def stop(self): self.stop_event.set()
