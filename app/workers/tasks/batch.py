# ============================================================
# app/workers/tasks/batch.py
# Celery tasks: split a batch into per-resume subtasks.
# ============================================================
import logging
from datetime import UTC, datetime
from uuid import UUID

from celery import chord, group
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.workers.celery_app import celery_app
from app.workers.tasks.resume import process_resume, validate_storage_path
from app.db.models.batch import Batch  # noqa: F401

logger = logging.getLogger(__name__)


def _sync_db_url() -> str:
    """Convert the async DATABASE_URL to a sync psycopg2 URL."""
    return settings.DATABASE_URL.replace("+asyncpg", "")


_sync_engine = create_engine(_sync_db_url(), pool_pre_ping=True)


def _load_verified_batch(session: Session, batch_id: str, tenant_id: str | None = None):
    """Load a batch and optionally verify the tenant carried by the task."""

    try:
        batch_uuid = UUID(batch_id)
    except ValueError as exc:
        raise ValueError("Invalid batch identifier") from exc

    batch = session.get(Batch, batch_uuid)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found")
    if tenant_id is not None and str(batch.tenant_id) != str(tenant_id):
        raise ValueError("Task tenant does not own the requested batch")
    return batch


@celery_app.task(bind=True, name="tasks.process_batch", max_retries=3)
def process_batch(self, batch_id: str, tenant_id: str | None = None) -> dict:
    """Coordinator task: split a batch into one subtask per resume."""
    from app.db.models.batch import Batch
    from app.db.models.resume import Resume

    try:
        with Session(_sync_engine) as session:
            batch = _load_verified_batch(session, batch_id, tenant_id)
            tenant_id = str(batch.tenant_id)

            resumes = (
                session.execute(
                    select(Resume).where(
                        Resume.batch_id == batch.id,
                    )
                )
                .scalars()
                .all()
            )

            if any(resume.tenant_id != batch.tenant_id for resume in resumes):
                raise ValueError("Batch contains a resume from another tenant")
            for resume in resumes:
                validate_storage_path(resume.storage_path, resume.tenant_id, batch.id)

            if not resumes:
                batch.status = "completed"
                batch.completed_at = datetime.now(UTC)
                session.commit()
                return {"batch_id": batch_id, "total_resumes": 0}

            session.execute(
                update(Batch)
                .where(Batch.id == batch.id)
                .values(status="processing", total_resumes=len(resumes))
            )
            session.commit()

            job = group(
                process_resume.s(
                    batch_id=str(batch.id),
                    resume_id=str(r.id),
                    storage_path=r.storage_path,
                    file_name=r.file_name,
                    tenant_id=tenant_id,
                )
                for r in resumes
            )

            chord(job)(
                finalize_batch.s(
                    batch_id=str(batch.id),
                    tenant_id=tenant_id,
                )
            )

        logger.info("Dispatched %d resume tasks for batch %s", len(resumes), batch_id)
        return {"batch_id": batch_id, "total_resumes": len(resumes)}

    except Exception as exc:
        logger.exception("process_batch failed for %s", batch_id)
        raise self.retry(exc=exc, countdown=30) from exc


@celery_app.task(name="tasks.finalize_batch")
def finalize_batch(results: list, batch_id: str, tenant_id: str | None = None) -> dict:
    """Chord callback: runs once every resume subtask has finished."""
    from app.db.models.resume import Resume

    with Session(_sync_engine) as session:
        try:
            batch = _load_verified_batch(session, batch_id, tenant_id)
        except ValueError as exc:
            if str(exc) == f"Batch {batch_id} not found":
                return {"batch_id": batch_id, "status": "not_found"}
            raise

        resumes = (
            session.execute(
                select(Resume).where(Resume.batch_id == batch.id)
            )
            .scalars()
            .all()
        )
        if any(resume.tenant_id != batch.tenant_id for resume in resumes):
            raise ValueError("Batch contains a resume from another tenant")
        statuses = [resume.status for resume in resumes]

        completed = sum(1 for s in statuses if s == "completed")
        failed = sum(1 for s in statuses if s == "failed")

        batch.completed = completed
        batch.failed = failed
        batch.status = "completed" if failed < len(statuses) else "failed"
        batch.completed_at = datetime.now(UTC)
        session.commit()

    logger.info("Batch %s finished: %d ok, %d failed", batch_id, completed, failed)
    return {
        "batch_id": batch_id,
        "completed": completed,
        "failed": failed,
        "status": "completed",
    }
