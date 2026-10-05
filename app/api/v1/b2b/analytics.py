# ============================================================
# app/api/v1/b2b/analytics.py
# Analytics endpoints for batches and tenant overview.
# ============================================================
import statistics
import uuid
from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_b2b_user, get_tenant_db
from app.db.models.batch import Batch
from app.db.models.resume import Resume
from app.db.models.user import User
from app.schemas.analytics import (
    BatchAnalytics,
    KeywordFrequency,
    ScoreDistribution,
    TenantOverview,
)

router = APIRouter(prefix="/b2b/analytics", tags=["B2B - Analytics"])


def _level_from_score(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "average"
    if score >= 40:
        return "below_average"
    return "weak"


def _build_distribution(scores: list[float]) -> ScoreDistribution:
    dist = ScoreDistribution()
    for s in scores:
        level = _level_from_score(float(s))
        setattr(dist, level, getattr(dist, level) + 1)
    return dist


def _top_missing(resumes: list[Resume], limit: int = 15) -> list[KeywordFrequency]:
    counter: Counter[str] = Counter()
    for r in resumes:
        for kw in r.missing_keywords or []:
            if isinstance(kw, str):
                counter[kw.lower()] += 1
    return [KeywordFrequency(keyword=k, count=c) for k, c in counter.most_common(limit)]


# ------------------------------------------------------------
# Single batch analytics
# ------------------------------------------------------------
@router.get("/batches/{batch_id}", response_model=BatchAnalytics)
async def batch_analytics(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> BatchAnalytics:
    """Return analytics for a single batch."""
    batch = (await db.execute(select(Batch).where(Batch.id == batch_id))).scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    resumes = (await db.execute(select(Resume).where(Resume.batch_id == batch_id))).scalars().all()

    scores = [r.ats_score for r in resumes if r.ats_score is not None]
    pending = sum(1 for r in resumes if r.status in ("pending", "processing"))

    if scores:
        avg = round(statistics.mean(scores), 2)
        median = round(statistics.median(scores), 2)
        mn = round(min(scores), 2)
        mx = round(max(scores), 2)
    else:
        avg = median = mn = mx = None

    completion_rate = (batch.completed / batch.total_resumes) if batch.total_resumes else 0.0

    return BatchAnalytics(
        batch_id=str(batch.id),
        job_title=batch.job_title,
        status=batch.status,
        total_resumes=batch.total_resumes,
        completed=batch.completed,
        failed=batch.failed,
        pending=pending,
        avg_score=avg,
        median_score=median,
        min_score=mn,
        max_score=mx,
        score_distribution=_build_distribution(scores),
        top_missing_keywords=_top_missing(resumes),
        completion_rate=round(completion_rate, 4),
    )


# ------------------------------------------------------------
# Tenant overview
# ------------------------------------------------------------
@router.get("/overview", response_model=TenantOverview)
async def tenant_overview(
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> TenantOverview:
    """Aggregate analytics across all batches for this tenant."""
    batches = (
        (await db.execute(select(Batch).order_by(Batch.created_at.desc()).limit(100)))
        .scalars()
        .all()
    )

    if not batches:
        return TenantOverview(
            tenant_id=str(user.tenant_id),
            total_batches=0,
            total_resumes=0,
            total_completed=0,
            total_failed=0,
            avg_ats_score=None,
            score_distribution=ScoreDistribution(),
            top_missing_keywords=[],
            recent_batches=[],
        )

    batch_ids = [b.id for b in batches]
    resumes = (
        (await db.execute(select(Resume).where(Resume.batch_id.in_(batch_ids)))).scalars().all()
    )

    scores = [r.ats_score for r in resumes if r.ats_score is not None]
    avg_score = round(statistics.mean(scores), 2) if scores else None

    recent = [
        {
            "id": str(b.id),
            "job_title": b.job_title,
            "status": b.status,
            "total_resumes": b.total_resumes,
            "completed": b.completed,
            "failed": b.failed,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in batches[:10]
    ]

    return TenantOverview(
        tenant_id=str(user.tenant_id),
        total_batches=len(batches),
        total_resumes=sum(b.total_resumes for b in batches),
        total_completed=sum(b.completed for b in batches),
        total_failed=sum(b.failed for b in batches),
        avg_ats_score=avg_score,
        score_distribution=_build_distribution(scores),
        top_missing_keywords=_top_missing(resumes),
        recent_batches=recent,
    )
