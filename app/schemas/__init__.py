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
from app.schemas.settings import (
    ConnectionTestResult,
    LLMSettingsRead,
    LLMSettingsUpdate,
    ProviderInfo,
    ProvidersListResponse,
)

__all__ = [
    # Analysis
    "AnalysisRequest",
    "AnalysisResponse",
    # Analytics
    "BatchAnalytics",
    "KeywordFrequency",
    "ScoreDistribution",
    "TenantOverview",
    # Auth
    "TenantRegister",
    "Token",
    "UserCreate",
    "UserRead",
    # Batch
    "BatchCreate",
    "BatchRead",
    "ResumeRead",
    # Settings
    "ConnectionTestResult",
    "LLMSettingsRead",
    "LLMSettingsUpdate",
    "ProviderInfo",
    "ProvidersListResponse",
]