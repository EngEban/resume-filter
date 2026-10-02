# ============================================================
# app/core/logging.py
# Structured logging setup using structlog.
# ============================================================
import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def _add_app_context(
    logger: Any,
    method_name: str,
    event_dict: dict,
) -> dict:
    """Inject static application context into every log entry."""
    event_dict["app"] = settings.APP_NAME
    event_dict["env"] = settings.APP_ENV
    return event_dict


def configure_logging() -> None:
    """
    Configure structlog + stdlib logging.

    In development: pretty, colorized console output.
    In production: JSON output for log aggregators.
    """
    # ---------- Shared processors ----------
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_app_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # ---------- Renderer ----------
    if settings.is_development:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    # ---------- structlog configuration ----------
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ---------- stdlib logging configuration ----------
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Silence noisy libraries
    for noisy in ("uvicorn.access", "httpx", "httpcore", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)