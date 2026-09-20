import json
import logging
import uuid

import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.app.api import router
from apps.api.app.config import get_settings
from apps.api.app.db.base import SessionLocal, engine
from apps.api.app.services import NotFoundError, dependency_status


settings = get_settings()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if hasattr(record, "job_id"):
            payload["job_id"] = record.job_id
        if hasattr(record, "job_type"):
            payload["job_type"] = record.job_type
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=settings.log_level, handlers=[handler], force=True)
logger = logging.getLogger("nexora.api")

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
app = FastAPI(title=settings.app_name, version=settings.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled request error", extra={"request_id": request_id})
        raise
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(NotFoundError)
async def not_found(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": exc.code, "message": exc.message, "request_id": request.state.request_id}},
    )


@app.exception_handler(ValueError)
async def conflict(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=409,
        content={"error": {"code": "CONFLICT", "message": str(exc), "request_id": request.state.request_id}},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nexora-api", "version": settings.version}


@app.get("/ready")
async def ready():
    try:
        async with SessionLocal() as db:
            dependencies = await dependency_status(db, redis_client)
    except Exception:
        dependencies = {"postgres": "error", "redis": "error"}
    overall = "ready" if all(value == "ok" for value in dependencies.values()) else "not_ready"
    return JSONResponse(
        status_code=200 if overall == "ready" else 503,
        content={"status": overall, "dependencies": dependencies},
    )


app.include_router(router)


@app.on_event("shutdown")
async def shutdown():
    await redis_client.aclose()
    await engine.dispose()
