# ============================================================
# app/core/config.py
# Application Configuration (Pydantic Settings)
# ============================================================
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---------- Application ----------
    APP_NAME: str = "ResumeFilter"
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True

    SECRET_KEY: str = Field(..., min_length=32)
    MASTER_KEY: str = Field(..., min_length=32)

    # ---------- Database ----------
    POSTGRES_USER: str = "rf_user"
    POSTGRES_PASSWORD: str = "rf_pass"
    POSTGRES_DB: str = "rf_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str

    # ---------- Redis / Celery ----------
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    CELERY_CONCURRENCY: int = 4

    # ---------- Object Storage (SeaweedFS, S3-compatible) ----------
    S3_ENDPOINT: str = "seaweedfs:8333"
    S3_ACCESS_KEY: str = "any-key"
    S3_SECRET_KEY: str = "any-secret"
    S3_BUCKET: str = "resumes"
    S3_SECURE: bool = False
    S3_REGION: str = "us-east-1"

    # ---------- File Upload Limits ----------
    B2C_MAX_FILE_SIZE_MB: int = 10
    B2C_DAILY_LIMIT: int = 3
    B2B_MAX_BATCH_SIZE: int = 500
    B2B_MAX_FILE_SIZE_MB: int = 10

    # ---------- Rate Limiting ----------
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_B2C_ANALYZE: str = "5/minute"
    RATE_LIMIT_B2B_UPLOAD: str = "20/minute"
    RATE_LIMIT_DEFAULT: str = "120/minute"

    # ---------- Platform Default LLM ----------
    PLATFORM_LLM_PROVIDER: str = "groq"
    PLATFORM_LLM_MODEL: str = "groq/openai/gpt-oss-20b"
    PLATFORM_LLM_API_KEY: str = ""
    PLATFORM_LLM_BASE_URL: str | None = None

    # ---------- Ollama (local fallback) ----------
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"

    # ---------- CORS ----------
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # ---------- UI ----------
    UI_STORAGE_SECRET: str = "change-me-in-production"

    # ---------- Logging ----------
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS_ORIGINS to a list."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
