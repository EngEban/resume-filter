# ============================================================
# app/workers/tasks/resume.py
# Celery task: process one resume end-to-end.
# ============================================================
import asyncio
import logging
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _sync_db_url() -> str:
    """Convert the async DATABASE_URL to a sync psycopg2 URL."""
    return settings.DATABASE_URL.replace("+asyncpg", "")


_sync_engine = create_engine(_sync_db_url(), pool_pre_ping=True)


async def _process_resume_async(
    resume_id: str,
    storage_path: str,
    file_name: str,
) -> dict:
    """
    Async pipeline for a single resume:
      download -> extract text -> parse -> LLM analysis -> ATS score -> persist.
    """
    from app.db.models.batch import Batch
    from app.db.models.resume import Resume
    from app.db.models.tenant import Tenant
    from app.providers import get_provider
    from app.services.ats_engine import calculate_ats_score
    from app.services.feedback_generator import generate_suggestions
    from app.services.parser import extract_text, parse_resume_text
    from app.services.storage import download_file

    # --- Load resume, batch, and tenant (read-only) ---
    with Session(_sync_engine) as session:
        resume = session.get(Resume, UUID(resume_id))
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")
        batch = session.get(Batch, resume.batch_id)
        job_description = batch.job_description if batch else ""
        tenant = session.get(Tenant, resume.tenant_id) if resume.tenant_id else None

    # --- Download file from MinIO ---
    file_bytes = download_file(storage_path)

    # --- Extract text ---
    raw_text = extract_text(file_bytes, file_name)
    if not raw_text.strip():
        raise ValueError("Empty resume text after extraction")

    # --- Parse ---
    parsed = parse_resume_text(raw_text)

    # --- LLM analysis (uses tenant's key if configured, else platform) ---
    provider = get_provider(tenant=tenant)
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
        resume = session.get(Resume, UUID(resume_id))
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
) -> dict:
    """Process a single resume inside the Celery worker."""
    try:
        result = asyncio.run(_process_resume_async(resume_id, storage_path, file_name))
        return result
    except Exception as exc:
        logger.exception("process_resume failed for %s: %s", resume_id, exc)

        # Mark as failed in DB
        try:
            from app.db.models.resume import Resume

            with Session(_sync_engine) as session:
                resume = session.get(Resume, UUID(resume_id))
                if resume:
                    resume.status = "failed"
                    resume.error_message = str(exc)[:1000]
                    session.commit()
        except Exception:
            logger.exception("Failed to mark resume %s as failed", resume_id)

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=30 * (self.request.retries + 1)) from exc
