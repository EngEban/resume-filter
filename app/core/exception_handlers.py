# ============================================================
# app/core/exception_handlers.py
# Global exception handlers for FastAPI.
# ============================================================
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the app."""

    # ---------- Application exceptions ----------
    @app.exception_handler(AppException)
    async def handle_app_exception(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            "Application exception",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_code": exc.error_code,
                "status_code": exc.status_code,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                **exc.to_dict(),
                "request_id": request_id,
            },
        )

    # ---------- Validation errors ----------
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.info(
            "Validation error",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "errors": exc.errors(),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "Request validation failed.",
                "details": {"errors": exc.errors()},
                "request_id": request_id,
            },
        )

    # ---------- HTTP exceptions (404, 405, etc.) ----------
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": exc.detail,
                "request_id": request_id,
            },
            headers=getattr(exc, "headers", None),
        )

    # ---------- SQLAlchemy errors ----------
    @app.exception_handler(SQLAlchemyError)
    async def handle_db_error(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "Database error",
            extra={"request_id": request_id, "path": request.url.path},
        )
        message = "Database error."
        if settings.DEBUG:
            message = f"Database error: {exc!s}"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "database_error",
                "message": message,
                "request_id": request_id,
            },
        )

    # ---------- Catch-all ----------
    @app.exception_handler(Exception)
    async def handle_unhandled(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "Unhandled exception",
            extra={"request_id": request_id, "path": request.url.path},
        )
        message = "Internal server error."
        if settings.DEBUG:
            message = f"{exc.__class__.__name__}: {exc!s}"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": message,
                "request_id": request_id,
            },
        )