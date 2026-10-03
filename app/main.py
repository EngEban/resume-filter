# ============================================================
# app/main.py
# FastAPI Application Entry Point
# ============================================================
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

# Configure logging before anything else.
configure_logging()
logger = get_logger(__name__)


# ------------------------------------------------------------
# Lifespan
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown."""
    logger.info(
        "application_starting",
        app=settings.APP_NAME,
        env=settings.APP_ENV,
    )

    if settings.DEBUG:
        # Auto-create missing tables (development only).
        try:
            from app.db.base import Base
            from app.db.models import (  # noqa: F401
                Analysis,
                Batch,
                Resume,
                Tenant,
                User,
            )
            from app.db.session import engine

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("database_tables_ensured")
        except Exception as exc:
            logger.warning("table_creation_failed", error=str(exc))

        logger.info("docs_available", url="http://localhost:8000/docs")
        logger.info("platform_llm", provider=settings.PLATFORM_LLM_PROVIDER)

    yield

    logger.info("application_shutting_down")


# ------------------------------------------------------------
# Application Factory
# ------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="AI-powered resume screening and ATS scoring system.",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )

    # ---------- Rate limiting ----------
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # ---------- Middleware ----------
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- Exception handlers ----------
    register_exception_handlers(app)

    # ---------- Root health (simple liveness for orchestrators) ----------
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "env": settings.APP_ENV,
        }

    @app.get("/", tags=["Root"])
    async def root() -> dict:
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "docs": "/docs",
            "ui": "/ui",
            "health": "/health",
            "api_health": "/api/v1/health/full",
        }

    # ---------- Routers ----------
    from app.api.v1.router import api_router

    app.include_router(api_router, prefix="/api/v1")

    # ---------- UI (NiceGUI) ----------
    if settings.APP_ENV != "test":
        from ui.main import register_ui

        register_ui(app)

    return app


# ------------------------------------------------------------
# Instance
# ------------------------------------------------------------
app = create_app()
