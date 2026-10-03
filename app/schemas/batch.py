# ============================================================
# app/schemas/batch.py
# Pydantic schemas for B2B batches.
# ============================================================
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BatchCreate(BaseModel):
    """Metadata when creating a batch (files uploaded separately)."""
    job_title: str = Field(..., min_length=2, max_length=255)
    job_description: str = Field(..., min_length=20)
    job_requirements: str | None = None


class BatchRead(BaseModel):
    """Batch status and progress."""
    id: UUID
    tenant_id: UUID
    job_title: str
    status: str
    total_resumes: int
    completed: int
    failed: int
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResumeRead(BaseModel):
    """Single resume result within a batch."""
    id: UUID
    file_name: str
    candidate_name: str | None = None
    candidate_email: str | None = None
    ats_score: float | None = None
    status: str
    missing_keywords: list | None = None
    suggestions: list | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
