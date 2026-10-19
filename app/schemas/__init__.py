# ============================================================
# app/schemas/__init__.py
# Export all schemas for easy imports.
# ============================================================
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.analytics import (
    BatchAnalytics,
    KeywordFrequency,
    ScoreDistribution,
    TenantOverview,
)
from app.schemas.auth import TenantRegister, Token, UserCreate, UserRead
from app.schemas.batch import BatchCreate, BatchRead, ResumeRead

__all__ = [
    # Analysis
    "AnalysisRequest",
    "AnalysisResponse",
    # Analytics
    "BatchAnalytics",
    # Batch
    "BatchCreate",
    "BatchRead",
    "KeywordFrequency",
    "ResumeRead",
    "ScoreDistribution",
    "TenantOverview",
    # Auth
    "TenantRegister",
    "Token",
    "UserCreate",
    "UserRead",
]
