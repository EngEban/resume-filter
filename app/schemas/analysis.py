# ============================================================
# app/schemas/analysis.py
# Pydantic schemas for B2C single-resume analysis.
# ============================================================
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Payload for a B2C analysis request."""

    resume_text: str = Field(..., min_length=50)
    job_description: str = Field(..., min_length=20)


class AnalysisResponse(BaseModel):
    """Result of a B2C analysis."""

    id: UUID | None = None
    ats_score: float
    level: str
    level_label: str
    breakdown: dict
    matched_keywords: list[str] = []
    missing_keywords: list[str] = []
    suggestions: list[dict] = []
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
