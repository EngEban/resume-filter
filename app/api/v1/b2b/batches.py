# ============================================================
# app/api/v1/b2b/batches.py
# B2B batch upload, status, export, and reprocessing endpoints.
# ============================================================
import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.b2b.authorization import get_tenant_batch
from app.core.config import settings
from app.core.dependencies import get_tenant_db, require_batch_operator
from app.db.models.batch import Batch
from app.db.models.resume import Resume
from app.db.models.user import User
from app.schemas.batch import BatchRead, ResumeRead
from app.services.excel_export import build_batch_workbook
from app.services.limits import check_batch_size
from app.services.pdf_export import build_batch_pdf
from app.services.storage import delete_file, upload_file
from app.workers.tasks.batch import process_batch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2b/batches", tags=["B2B - Batches"])


# ============================================================
# Create batch
# ============================================================
@router.post("", response_model=BatchRead, status_code=status.HTTP_201_CREATED)
async def create_batch(
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
    job_title: Annotated[str, Form()],
    job_description: Annotated[str, Form()],
    job_requirements: Annotated[str | None, Form()] = None,
    files: Annotated[list[UploadFile] | None, File()] = None,
) -> BatchRead:
    """Upload a batch of resumes for a job description."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    check_batch_size(len(files), settings.B2B_MAX_BATCH_SIZE)
    max_bytes = settings.B2B_MAX_FILE_SIZE_MB * 1024 * 1024
    batch = Batch(
        tenant_id=user.tenant_id,
        job_title=job_title,
        job_description=job_description,
        job_requirements=job_requirements,
        status="pending",
        total_resumes=len(files),
    )
    db.add(batch)
    await db.flush()
    uploaded_paths: list[str] = []

    try:
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Every file must have a filename")
            safe_filename = os.path.basename(file.filename.replace("\\", "/"))
            if not safe_filename.lower().endswith((".pdf", ".docx")):
                raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
            data = await file.read()
            if not data:
                raise HTTPException(status_code=400, detail=f"{safe_filename} is empty")
            if len(data) > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"{safe_filename} exceeds {settings.B2B_MAX_FILE_SIZE_MB} MB",
                )
            object_name = f"{user.tenant_id}/{batch.id}/{uuid.uuid4()}_{safe_filename}"
            storage_path = upload_file(
                object_name=object_name,
                data=data,
                content_type=file.content_type or "application/octet-stream",
            )
            uploaded_paths.append(storage_path)
            db.add(
                Resume(
                    tenant_id=user.tenant_id,
                    batch_id=batch.id,
                    file_name=safe_filename,
                    storage_path=storage_path,
                    file_size=len(data),
                    status="pending",
                )
            )
    except Exception:
        for storage_path in uploaded_paths:
            delete_file(storage_path)
        raise

    await db.flush()
    await db.commit()
    await db.refresh(batch)
    process_batch.delay(str(batch.id), tenant_id=str(user.tenant_id))
    return BatchRead.model_validate(batch)


# ============================================================
# List batches
# ============================================================
@router.get("", response_model=list[BatchRead])
async def list_batches(
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    search: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[BatchRead]:
    """List batches for the tenant (paginated, filterable)."""
    stmt = select(Batch).where(Batch.tenant_id == user.tenant_id)
    if status_filter:
        stmt = stmt.where(Batch.status == status_filter)
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(func.lower(Batch.job_title).like(like))
    stmt = stmt.order_by(Batch.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return [BatchRead.model_validate(b) for b in result.scalars().all()]


# ============================================================
# Get batch
# ============================================================
@router.get("/{batch_id}", response_model=BatchRead)
async def get_batch(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> BatchRead:
    """Return a batch's status and progress."""
    batch = await get_tenant_batch(db, user.tenant_id, batch_id)
    return BatchRead.model_validate(batch)


# ============================================================
# List resumes in a batch
# ============================================================
@router.get("/{batch_id}/resumes", response_model=list[ResumeRead])
async def list_batch_resumes(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
    search: Annotated[str | None, Query()] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    min_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    sort: Annotated[
        Literal["score_desc", "score_asc", "name_asc", "recent"],
        Query(),
    ] = "score_desc",
) -> list[ResumeRead]:
    """List resumes in a batch with filtering and sorting."""
    await get_tenant_batch(db, user.tenant_id, batch_id)
    stmt = select(Resume).where(
        Resume.batch_id == batch_id,
        Resume.tenant_id == user.tenant_id,
    )

    if status_filter:
        stmt = stmt.where(Resume.status == status_filter)

    if min_score is not None:
        stmt = stmt.where(Resume.ats_score >= min_score)

    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Resume.candidate_name).like(like),
                func.lower(Resume.candidate_email).like(like),
                func.lower(Resume.file_name).like(like),
            )
        )

    if sort == "score_desc":
        stmt = stmt.order_by(Resume.ats_score.desc().nullslast())
    elif sort == "score_asc":
        stmt = stmt.order_by(Resume.ats_score.asc().nullsfirst())
    elif sort == "name_asc":
        stmt = stmt.order_by(Resume.candidate_name.asc().nullslast())
    else:
        stmt = stmt.order_by(Resume.created_at.desc())

    result = await db.execute(stmt)
    return [ResumeRead.model_validate(r) for r in result.scalars().all()]


# ============================================================
# Export to Excel
# ============================================================
@router.get("/{batch_id}/export.xlsx")
async def export_batch_xlsx(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> Response:
    """Export a batch's results as an Excel workbook."""
    batch = await get_tenant_batch(db, user.tenant_id, batch_id)

    resumes = (
        (
            await db.execute(
                select(Resume)
                .where(
                    Resume.batch_id == batch_id,
                    Resume.tenant_id == user.tenant_id,
                )
                .order_by(Resume.ats_score.desc().nullslast())
            )
        )
        .scalars()
        .all()
    )

    batch_dict = {
        "id": str(batch.id),
        "job_title": batch.job_title,
        "status": batch.status,
        "total_resumes": batch.total_resumes,
        "completed": batch.completed,
        "failed": batch.failed,
    }
    resume_dicts = [
        {
            "candidate_name": r.candidate_name,
            "candidate_email": r.candidate_email,
            "candidate_phone": r.candidate_phone,
            "ats_score": r.ats_score,
            "missing_keywords": r.missing_keywords,
            "matched_keywords": None,
            "status": r.status,
            "file_name": r.file_name,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in resumes
    ]

    xlsx_bytes = build_batch_workbook(batch_dict, resume_dicts)
    filename = f"batch_{str(batch.id)[:8]}_{datetime.now(UTC):%Y%m%d}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================================
# Export to PDF
# ============================================================
@router.get("/{batch_id}/export.pdf")
async def export_batch_pdf(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> Response:
    """Export a batch's results as a PDF report."""
    batch = await get_tenant_batch(db, user.tenant_id, batch_id)

    resumes = (
        (
            await db.execute(
                select(Resume)
                .where(
                    Resume.batch_id == batch_id,
                    Resume.tenant_id == user.tenant_id,
                )
                .order_by(Resume.ats_score.desc().nullslast())
            )
        )
        .scalars()
        .all()
    )

    batch_dict = {
        "id": str(batch.id),
        "job_title": batch.job_title,
        "status": batch.status,
        "total_resumes": batch.total_resumes,
        "completed": batch.completed,
        "failed": batch.failed,
    }
    resume_dicts = [
        {
            "candidate_name": r.candidate_name,
            "candidate_email": r.candidate_email,
            "ats_score": r.ats_score,
            "missing_keywords": r.missing_keywords,
            "status": r.status,
        }
        for r in resumes
    ]

    pdf_bytes = build_batch_pdf(batch_dict, resume_dicts)
    filename = f"batch_{str(batch.id)[:8]}_{datetime.now(UTC):%Y%m%d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================================
# Reprocess failed resumes
# ============================================================
@router.post("/{batch_id}/reprocess", response_model=BatchRead)
async def reprocess_batch(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> BatchRead:
    """Reprocess only the failed resumes in a batch."""
    batch = await get_tenant_batch(db, user.tenant_id, batch_id)

    failed_resumes = (
        (
            await db.execute(
                select(Resume).where(
                    Resume.batch_id == batch_id,
                    Resume.tenant_id == user.tenant_id,
                    Resume.status == "failed",
                )
            )
        )
        .scalars()
        .all()
    )

    if not failed_resumes:
        raise HTTPException(
            status_code=400,
            detail="No failed resumes to reprocess.",
        )

    for r in failed_resumes:
        r.status = "pending"
        r.error_message = None

    batch.status = "processing"
    batch.failed = 0
    batch.completed_at = None

    await db.flush()
    await db.refresh(batch)

    from celery import chord

    from app.workers.tasks.batch import finalize_batch
    from app.workers.tasks.resume import process_resume

    header = [
        process_resume.s(
            batch_id=str(batch.id),
            resume_id=str(r.id),
            storage_path=r.storage_path,
            file_name=r.file_name,
            tenant_id=str(user.tenant_id),
        )
        for r in failed_resumes
    ]
    await db.commit()
    chord(header)(
        finalize_batch.s(
            batch_id=str(batch.id),
            tenant_id=str(user.tenant_id),
        )
    )

    logger.info(
        "Reprocessing %d failed resumes for batch %s",
        len(failed_resumes),
        batch_id,
    )
    return BatchRead.model_validate(batch)
# ============================================================
# Delete a single batch (DB + storage files)
# ============================================================
@router.delete("/{batch_id}", status_code=status.HTTP_200_OK)
async def delete_batch(
    batch_id: uuid.UUID,
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> dict:
    """Delete a batch and all its resumes."""
    batch = await get_tenant_batch(db, user.tenant_id, batch_id)
    storage_paths = (
        (await db.execute(select(Resume.storage_path).where(Resume.batch_id == batch_id, Resume.tenant_id == user.tenant_id)))
        .scalars()
        .all()
    )
    resume_count = len(storage_paths)

    for path in storage_paths:
        try:
            delete_file(path)
        except Exception as exc:
            logger.warning("Failed to delete storage file %s: %s", path, exc)

    await db.delete(batch)
    await db.commit()

    return {"message": "Batch deleted.", "id": str(batch_id), "deleted_resumes": resume_count}

# ============================================================
# Delete all batches for the tenant
# ============================================================
@router.delete("", status_code=status.HTTP_200_OK)
async def clear_all_batches(
    user: Annotated[User, Depends(require_batch_operator)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> dict:
    """Delete ALL batches for the current tenant."""
    storage_paths = (
        (await db.execute(select(Resume.storage_path).where(Resume.tenant_id == user.tenant_id)))
        .scalars()
        .all()
    )
    batch_count_result = await db.execute(select(func.count(Batch.id)).where(Batch.tenant_id == user.tenant_id))
    batch_count = batch_count_result.scalar_one() or 0
    resume_count = len(storage_paths)

    for path in storage_paths:
        try:
            delete_file(path)
        except Exception as exc:
            logger.warning("Failed to delete storage file %s: %s", path, exc)

    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(Batch).where(Batch.tenant_id == user.tenant_id))
    await db.commit()

    return {"message": "All batches cleared.", "deleted_batches": batch_count, "deleted_resumes": resume_count}