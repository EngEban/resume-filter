# ============================================================
# app/core/rate_limit.py
# Rate limiting via slowapi (per-IP, configurable per endpoint).
# ============================================================
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings


def _key_func(request) -> str:
    """
    Identify the caller for rate limiting.

    Prefers a JWT user ID if present, falls back to IP.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        # Use the first 40 chars of the token to bucket users
        # without decoding it (fast + no crypto here).
        return f"token:{auth[7:47]}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=_key_func,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri=settings.REDIS_URL,
)


def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):
    """
    Custom handler so 429 responses match our error schema.
    Registered in app/main.py.
    """
    from fastapi.responses import JSONResponse

    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
            "request_id": request_id,
        },
    )