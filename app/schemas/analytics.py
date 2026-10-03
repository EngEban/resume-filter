# ============================================================
# app/schemas/analytics.py
# Pydantic schemas for batch analytics.
# ============================================================
from typing import Any

from pydantic import BaseModel


class ScoreDistribution(BaseModel):
    """Count of resumes per ATS level."""

    excellent: int = 0
    good: int = 0
    average: int = 0
    below_average: int = 0
    weak: int = 0


class KeywordFrequency(BaseModel):
    """A keyword and how often it appears as missing."""

    keyword: str
    count: int


class BatchAnalytics(BaseModel):
    """Analytics summary for a single batch."""

    batch_id: str
    job_title: str
    status: str

    total_resumes: int
    completed: int
    failed: int
    pending: int

    avg_score: float | None = None
    median_score: float | None = None
    min_score: float | None = None
    max_score: float | None = None

    score_distribution: ScoreDistribution
    top_missing_keywords: list[KeywordFrequency] = []

    completion_rate: float = 0.0


class TenantOverview(BaseModel):
    """High-level analytics across all of a tenant's batches."""

    tenant_id: str
    total_batches: int
    total_resumes: int
    total_completed: int
    total_failed: int

    avg_ats_score: float | None = None
    score_distribution: ScoreDistribution
    top_missing_keywords: list[KeywordFrequency] = []
    recent_batches: list[dict[str, Any]] = []
