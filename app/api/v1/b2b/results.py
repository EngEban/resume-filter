# ============================================================
# app/api/v1/b2b/results.py
# Per-resume reports + candidate comparison + PDF export.
# ============================================================
import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_b2b_user, get_tenant_db
from app.db.models.batch import Batch
from app.db.models.resume import Resume
from app.db.models.user import User
from app.services.excel_export import build_comparison_workbook
from app.services.pdf_export import build_resume_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2b/resumes", tags=["B2B - Results"])


# ============================================================
# Get single resume report
# ============================================================
@router.get("/{resume_id}")
async def get_resume_report(
    resume_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> dict:
    """Return a detailed report for a single resume."""
    resume = (
        await db.execute(select(Resume).where(Resume.id == resume_id))
    ).scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {
        "id": str(resume.id),
        "file_name": resume.file_name,
        "candidate_name": resume.candidate_name,
        "candidate_email": resume.candidate_email,
        "candidate_phone": resume.candidate_phone,
        "ats_score": resume.ats_score,
        "score_breakdown": resume.score_breakdown,
        "missing_keywords": resume.missing_keywords,
        "suggestions": resume.suggestions,
        "status": resume.status,
        "error_message": resume.error_message,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
    }


# ============================================================
# Export single resume report as PDF
# ============================================================
@router.get("/{resume_id}/report.pdf")
async def export_resume_pdf(
    resume_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> Response:
    """Export a single candidate's report as a PDF."""
    resume = (
        await db.execute(select(Resume).where(Resume.id == resume_id))
    ).scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    report = {
        "candidate_name": resume.candidate_name,
        "candidate_email": resume.candidate_email,
        "candidate_phone": resume.candidate_phone,
        "ats_score": resume.ats_score,
        "score_breakdown": resume.score_breakdown,
        "missing_keywords": resume.missing_keywords,
        "suggestions": resume.suggestions,
    }

    pdf_bytes = build_resume_pdf(report)
    name = (resume.candidate_name or "candidate").replace(" ", "_")
    filename = f"{name}_{str(resume.id)[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================================
# Compare candidates in a batch (side-by-side)
# ============================================================
@router.get("/compare")
async def compare_candidates(
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
    batch_id: Annotated[uuid.UUID, Query()],
    limit: Annotated[int, Query(ge=2, le=20)] = 5,
) -> dict:
    """Return the top-N candidates of a batch, side by side."""
    resumes = (
        await db.execute(
            select(Resume)
            .where(Resume.batch_id == batch_id)
            .order_by(Resume.ats_score.desc().nullslast())
            .limit(limit)
        )
    ).scalars().all()

    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")

    return {
        "batch_id": str(batch_id),
        "count": len(resumes),
        "candidates": [
            {
                "id": str(r.id),
                "name": r.candidate_name or "—",
                "email": r.candidate_email,
                "phone": r.candidate_phone,
                "ats_score": r.ats_score,
                "score_breakdown": r.score_breakdown or {},
                "missing_keywords": (r.missing_keywords or [])[:20],
                "status": r.status,
            }
            for r in resumes
        ],
    }


# ============================================================
# Export candidate comparison as Excel
# ============================================================
@router.get("/compare/export.xlsx")
async def export_comparison_xlsx(
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
    batch_id: Annotated[uuid.UUID, Query()],
    limit: Annotated[int, Query(ge=2, le=20)] = 10,
) -> Response:
    """Export a candidate comparison as an Excel workbook."""
    batch = (
        await db.execute(select(Batch).where(Batch.id == batch_id))
    ).scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    resumes = (
        await db.execute(
            select(Resume)
            .where(Resume.batch_id == batch_id)
            .order_by(Resume.ats_score.desc().nullslast())
            .limit(limit)
        )
    ).scalars().all()

    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")

    batch_dict = {
        "id": str(batch.id),
        "job_title": batch.job_title,
        "status": batch.status,
    }
    resume_dicts = [
        {
            "candidate_name": r.candidate_name,
            "candidate_email": r.candidate_email,
            "candidate_phone": r.candidate_phone,
            "ats_score": r.ats_score,
            "missing_keywords": r.missing_keywords,
            "status": r.status,
        }
        for r in resumes
    ]

    xlsx_bytes = build_comparison_workbook(batch_dict, resume_dicts)
    filename = f"compare_{str(batch.id)[:8]}_{datetime.now(UTC):%Y%m%d}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
