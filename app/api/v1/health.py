# ============================================================
# app/api/v1/health.py
# Comprehensive health checks (DB, Redis, MinIO, LLM).
# ============================================================
import logging
import time
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(tags=["Health"])

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Individual checks
# ------------------------------------------------------------
async def _check_database() -> dict[str, Any]:
    from app.db.session import engine

    started = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:
        logger.warning("DB health check failed: %s", exc)
        return {"status": "error", "error": str(exc)}


async def _check_redis() -> dict[str, Any]:
    import redis.asyncio as aioredis

    from app.core.config import settings

    started = time.perf_counter()
    client = None
    try:
        client = aioredis.from_url(settings.REDIS_URL, socket_timeout=3)
        pong = await client.ping()
        return {
            "status": "ok" if pong else "error",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        return {"status": "error", "error": str(exc)}
    finally:
        if client is not None:
            await client.aclose()


def _check_minio() -> dict[str, Any]:
    from app.services.storage import get_client

    started = time.perf_counter()
    try:
        client = get_client()
        # Listing buckets is cheap and confirms connectivity.
        list(client.list_buckets())
        return {
            "status": "ok",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as exc:
        logger.warning("MinIO health check failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def _check_llm_config() -> dict[str, Any]:
    from app.core.config import settings

    configured = bool(
        settings.PLATFORM_LLM_API_KEY
        and settings.PLATFORM_LLM_API_KEY != "your-groq-api-key-here"
    )
    return {
        "status": "ok" if configured else "unconfigured",
        "provider": settings.PLATFORM_LLM_PROVIDER,
        "model": settings.PLATFORM_LLM_MODEL,
    }


# ------------------------------------------------------------
# Simple liveness probe
# ------------------------------------------------------------
@router.get("/health/live", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    """Returns 200 if the process is alive. No dependencies checked."""
    return {"status": "alive"}


# ------------------------------------------------------------
# Readiness probe
# ------------------------------------------------------------
@router.get("/health/ready", summary="Readiness probe")
async def readiness() -> JSONResponse:
    """Returns 200 if all critical dependencies are healthy."""
    checks = {
        "database": await _check_database(),
        "redis": await _check_redis(),
    }
    ok = all(c["status"] == "ok" for c in checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ready" if ok else "not_ready", "checks": checks},
    )


# ------------------------------------------------------------
# Full health report
# ------------------------------------------------------------
@router.get("/health/full", summary="Full health report")
async def full_health() -> JSONResponse:
    """Full diagnostic report: DB, Redis, MinIO, and LLM configuration."""
    checks = {
        "database": await _check_database(),
        "redis": await _check_redis(),
        "minio": _check_minio(),
        "llm": _check_llm_config(),
    }
    critical = ("database", "redis", "minio")
    ok = all(checks[k]["status"] == "ok" for k in critical)
    return JSONResponse(
        status_code=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if ok else "degraded",
            "checks": checks,
        },
    )