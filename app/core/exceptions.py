# ============================================================
# app/core/exceptions.py
# Application exception hierarchy.
# ============================================================
from typing import Any


class AppException(Exception):
    """Base application exception."""

    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API responses."""
        payload: dict[str, Any] = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload


# ------------------------------------------------------------
# 4xx - Client errors
# ------------------------------------------------------------
class BadRequestError(AppException):
    status_code = 400
    error_code = "bad_request"
    message = "Invalid request."


class UnauthorizedError(AppException):
    status_code = 401
    error_code = "unauthorized"
    message = "Authentication required."


class ForbiddenError(AppException):
    status_code = 403
    error_code = "forbidden"
    message = "Permission denied."


class NotFoundError(AppException):
    status_code = 404
    error_code = "not_found"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = 409
    error_code = "conflict"
    message = "Resource already exists."


class UnprocessableEntityError(AppException):
    status_code = 422
    error_code = "unprocessable_entity"
    message = "The request could not be processed."


class LimitExceededError(AppException):
    status_code = 429
    error_code = "limit_exceeded"
    message = "Usage limit exceeded."


# ------------------------------------------------------------
# 5xx - Server errors
# ------------------------------------------------------------
class ProviderError(AppException):
    status_code = 502
    error_code = "provider_error"
    message = "External provider error."


class StorageError(AppException):
    status_code = 502
    error_code = "storage_error"
    message = "Object storage error."


class DatabaseError(AppException):
    status_code = 500
    error_code = "database_error"
    message = "Database error."


class ConfigurationError(AppException):
    status_code = 500
    error_code = "configuration_error"
    message = "Server configuration error."


# ------------------------------------------------------------
# Domain-specific
# ------------------------------------------------------------
class InvalidAPIKeyError(BadRequestError):
    error_code = "invalid_api_key"
    message = "The provided API key is invalid."


class BatchProcessingError(AppException):
    status_code = 500
    error_code = "batch_processing_error"
    message = "Failed to process the batch."