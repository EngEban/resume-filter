# ============================================================
# app/workers/tasks/resume.py
# Celery task: process one resume end-to-end.
# ============================================================
import asyncio
import logging
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _sync_db_url() -> str:
    """Convert the async DATABASE_URL to a sync psycopg2 URL."""
    return settings.DATABASE_URL.replace("+asyncpg", "")


_sync_engine = create_engine(_sync_db_url(), pool_pre_ping=True)


def validate_storage_path(storage_path: str, tenant_id: UUID, batch_id: UUID) -> None:
    """Ensure a stored object remains inside its tenant and batch prefix."""
    expected_prefix = f"{settings.S3_BUCKET}/{tenant_id}/{batch_id}/"
    if not storage_path.startswith(expected_prefix):
        raise ValueError("Resume storage path does not match its tenant and batch")


def _load_verified_resume(
    session: Session,
    batch_id: str,
    resume_id: str,
    storage_path: str,
    file_name: str,
    tenant_id: str | None = None,
    *,
    lock: bool = False,
):
    """Load a resume only after validating all task-to-database relationships."""
    from app.db.models.batch import Batch
    from app.db.models.resume import Resume
    from app.db.models.tenant import Tenant

    try:
        batch_uuid = UUID(batch_id)
        resume_uuid = UUID(resume_id)
    except ValueError as exc:
        raise ValueError("Invalid batch or resume identifier") from exc

    if lock:
        resume = (
            session.execute(
                select(Resume).where(Resume.id == resume_uuid).with_for_update()
            )
            .scalars()
            .one_or_none()
        )
    else:
        resume = session.get(Resume, resume_uuid)
    if not resume:
        raise ValueError(f"Resume {resume_id} not found")

    batch = session.get(Batch, batch_uuid)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found")
    if resume.batch_id != batch.id:
        raise ValueError("Resume does not belong to the requested batch")
    if resume.tenant_id != batch.tenant_id:
        raise ValueError("Resume and batch belong to different tenants")
    if tenant_id is not None and str(batch.tenant_id) != str(tenant_id):
        raise ValueError("Task tenant does not own the requested batch")
    if resume.storage_path != storage_path:
        raise ValueError("Task storage path does not match the stored resume")
    if resume.file_name != file_name:
        raise ValueError("Task file name does not match the stored resume")

    validate_storage_path(resume.storage_path, resume.tenant_id, batch.id)
    tenant = session.get(Tenant, resume.tenant_id)
    return resume, batch, tenant


def _get_or_create_loop() -> asyncio.AbstractEventLoop:
    """
    Return the persistent event loop for this worker process.

    Creates one if none exists or if the current one is closed.
    """
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop is closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def _process_resume_async(
    resume_id: str,
    storage_path: str,
    file_name: str,
    *,
    batch_id: str,
    tenant_id: str | None = None,
    allow_retry: bool = False,
) -> dict:
    """
    Async pipeline for a single resume:
      download -> extract text -> parse -> LLM analysis -> ATS score -> persist.
    """
    from app.providers import get_provider
    from app.services.ats_engine import calculate_ats_score
    from app.services.feedback_generator import generate_suggestions
    from app.services.parser import extract_text, parse_resume_text
    from app.services.storage import download_file

    # --- Validate and claim the resume before doing external work ---
    with Session(_sync_engine) as session:
        resume, batch, _tenant = _load_verified_resume(
            session,
            batch_id=batch_id,
            resume_id=resume_id,
            storage_path=storage_path,
            file_name=file_name,
            tenant_id=tenant_id,
            lock=True,
        )

        if resume.status == "completed":
            return {
                "resume_id": resume_id,
                "ats_score": resume.ats_score,
                "status": "completed",
            }
        if resume.status == "processing":
            return {
                "resume_id": resume_id,
                "status": "skipped",
                "reason": "already_processing",
            }
        if resume.status == "failed" and not allow_retry:
            return {
                "resume_id": resume_id,
                "status": "skipped",
                "reason": "requires_reprocess",
            }

        resume.status = "processing"
        session.commit()

        trusted_storage_path = resume.storage_path
        trusted_file_name = resume.file_name
        job_description = batch.job_description
        # Provider credentials and endpoint are platform-managed; tenant is
        # retained above for ownership and audit context only.
        provider = get_provider()

    # --- Download file from object storage ---
    file_bytes = download_file(trusted_storage_path)

    # --- Extract text ---
    raw_text = extract_text(file_bytes, trusted_file_name)
    if not raw_text.strip():
        raise ValueError("Empty resume text after extraction")

    # --- Parse ---
    parsed = parse_resume_text(raw_text)

    # --- LLM analysis ---
    llm_analysis, suggestions = await generate_suggestions(
        provider=provider,
        resume_text=raw_text,
        job_description=job_description,
        parsed=parsed,
    )

    # --- ATS score ---
    score = calculate_ats_score(
        parsed_resume=parsed,
        raw_text=raw_text,
        job_description=job_description,
        llm_analysis=llm_analysis,
    )

    # --- Persist result ---
    with Session(_sync_engine) as session:
        resume, batch, _ = _load_verified_resume(
            session,
            batch_id=batch_id,
            resume_id=resume_id,
            storage_path=trusted_storage_path,
            file_name=trusted_file_name,
            tenant_id=tenant_id,
        )
        if resume.status != "processing":
            raise ValueError("Resume processing state changed before persistence")
        resume.candidate_name = parsed.get("candidate_name")
        resume.candidate_email = parsed.get("email")
        resume.candidate_phone = parsed.get("phone")
        resume.raw_text = raw_text
        resume.parsed_data = parsed
        resume.ats_score = score.total
        resume.score_breakdown = score.breakdown.__dict__
        resume.missing_keywords = score.missing_keywords
        resume.suggestions = suggestions
        resume.status = "completed"
        session.commit()

    return {
        "resume_id": resume_id,
        "ats_score": score.total,
        "status": "completed",
    }


@celery_app.task(
    bind=True,
    name="tasks.process_resume",
    max_retries=3,
    acks_late=True,
)
def process_resume(
    self,
    batch_id: str,
    resume_id: str,
    storage_path: str,
    file_name: str,
    tenant_id: str | None = None,
) -> dict:
    """
    Process a single resume inside the Celery worker.

    Uses a PERSISTENT event loop (not asyncio.run) to avoid
    the "Event loop is closed" error from cached HTTP clients.
    """
    try:
        loop = _get_or_create_loop()
        result = loop.run_until_complete(
            _process_resume_async(
                resume_id,
                storage_path,
                file_name,
                batch_id=batch_id,
                tenant_id=tenant_id,
                allow_retry=self.request.retries > 0,
            )
        )
        return result
    except Exception as exc:
        logger.exception("process_resume failed for %s: %s", resume_id, exc)

        # Mark as failed in DB (best-effort)
        try:
            with Session(_sync_engine) as session:
                resume, _, _ = _load_verified_resume(
                    session,
                    batch_id=batch_id,
                    resume_id=resume_id,
                    storage_path=storage_path,
                    file_name=file_name,
                    tenant_id=tenant_id,
                )
                if resume.status == "processing":
                    resume.status = "failed"
                    resume.error_message = str(exc)[:1000]
                    session.commit()
        except Exception:
            logger.exception("Failed to mark resume %s as failed", resume_id)

        # Terminal failure
        if self.request.retries >= self.max_retries:
            return {
                "resume_id": resume_id,
                "status": "failed",
                "error": str(exc)[:1000],
            }

        # Retry with exponential backoff
        raise self.retry(
            exc=exc, countdown=30 * (self.request.retries + 1)
        ) from exc
