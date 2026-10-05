# ============================================================
# app/api/v1/b2c/analyze.py
# B2C single-resume analysis endpoint (file upload).
# ============================================================
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_b2c_user
from app.db.models.analysis import Analysis
from app.db.models.user import User
from app.db.session import get_db
from app.providers import get_provider
from app.schemas.analysis import AnalysisResponse
from app.services.ats_engine import calculate_ats_score
from app.services.feedback_generator import generate_suggestions
from app.services.limits import check_b2c_daily_limit
from app.services.parser import extract_text, parse_resume_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2c", tags=["B2C - Individuals"])

ALLOWED_EXTENSIONS = (".pdf", ".docx")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    user: Annotated[User, Depends(get_current_b2c_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    job_description: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
) -> AnalysisResponse:
    """
    Analyze an uploaded resume (PDF/DOCX) against a job description.

    The resume file is processed in-memory and is NOT stored.
    """
    # ---------- 1. Validate file ----------
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename_lower = file.filename.lower()
    if not filename_lower.endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    if len(job_description.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 20 characters.",
        )

    # ---------- 2. Read and size-check ----------
    max_bytes = settings.B2C_MAX_FILE_SIZE_MB * 1024 * 1024
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=(f"File exceeds the maximum size of " f"{settings.B2C_MAX_FILE_SIZE_MB} MB."),
        )

    # ---------- 3. Extract text ----------
    try:
        resume_text = extract_text(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to extract text from %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded file.",
        ) from exc

    if len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract enough text from the file. "
                "If it is a scanned PDF, please upload a text-based PDF or DOCX."
            ),
        )

    # ---------- 4. Enforce daily limit ----------
    await check_b2c_daily_limit(user.id, db, limit=settings.B2C_DAILY_LIMIT)

    # ---------- 5. Parse ----------
    parsed = parse_resume_text(resume_text)

    # ---------- 6. LLM analysis ----------
    provider = get_provider(tenant=None)
    try:
        llm_analysis, suggestions = await generate_suggestions(
            provider=provider,
            resume_text=resume_text,
            job_description=job_description,
            parsed=parsed,
        )
    except Exception as exc:
        logger.exception("LLM analysis failed: %s", exc)
        raise HTTPException(status_code=502, detail="LLM provider error") from exc

    # ---------- 7. ATS score ----------
    score = calculate_ats_score(
        parsed_resume=parsed,
        raw_text=resume_text,
        job_description=job_description,
        llm_analysis=llm_analysis,
    )

    # ---------- 8. Persist ----------
    analysis = Analysis(
        user_id=user.id,
        resume_text=resume_text,
        job_description=job_description,
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
