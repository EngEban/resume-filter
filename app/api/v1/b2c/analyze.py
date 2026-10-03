# ============================================================
# app/api/v1/b2c/analyze.py
# B2C single-resume analysis endpoint.
# ============================================================
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_b2c_user
from app.db.models.analysis import Analysis
from app.db.models.user import User
from app.db.session import get_db
from app.providers import get_provider
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.ats_engine import calculate_ats_score
from app.services.feedback_generator import generate_suggestions
from app.services.limits import check_b2c_daily_limit
from app.services.parser import parse_resume_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2c", tags=["B2C - Individuals"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    payload: AnalysisRequest,
    user: Annotated[User, Depends(get_current_b2c_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AnalysisResponse:
    """Analyze a single resume against a job description."""
    await check_b2c_daily_limit(user.id, db, limit=settings.B2C_DAILY_LIMIT)

    parsed = parse_resume_text(payload.resume_text)

    provider = get_provider(tenant=None)
    try:
        llm_analysis, suggestions = await generate_suggestions(
            provider=provider,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            parsed=parsed,
        )
    except Exception as exc:
        logger.exception("LLM analysis failed: %s", exc)
        raise HTTPException(status_code=502, detail="LLM provider error") from exc

    score = calculate_ats_score(
        parsed_resume=parsed,
        raw_text=payload.resume_text,
        job_description=payload.job_description,
        llm_analysis=llm_analysis,
    )

    analysis = Analysis(
        user_id=user.id,
        resume_text=payload.resume_text,
        job_description=payload.job_description,
        ats_score=score.total,
        breakdown=score.breakdown.__dict__,
        missing_keywords=score.missing_keywords,
        suggestions=suggestions,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return AnalysisResponse(
        id=analysis.id,
        ats_score=score.total,
        level=score.level,
        level_label=score.level_label,
        breakdown=score.breakdown.__dict__,
        matched_keywords=score.matched_keywords,
        missing_keywords=score.missing_keywords,
        suggestions=suggestions,
        created_at=analysis.created_at,
    )
