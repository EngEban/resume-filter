from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.config import settings
from app.db.models.batch import Batch
from app.db.models.resume import Resume
from app.db.models.tenant import Tenant
from app.workers.tasks import batch as batch_task
from app.workers.tasks import resume as resume_task


class FakeWorkerSession:
    def __init__(self, *, batch, resume, tenant):
        self.batch = batch
        self.resume = resume
        self.tenant = tenant

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def get(self, model, _identifier):
        return {
            Batch: self.batch,
            Resume: self.resume,
            Tenant: self.tenant,
        }.get(model)

    def execute(self, _statement):
        return SimpleNamespace(
            scalars=lambda: SimpleNamespace(one_or_none=lambda: self.resume)
        )

    def commit(self):
        return None


def _storage_path(tenant_id, batch_id, file_name="resume.pdf"):
    return f"{settings.S3_BUCKET}/{tenant_id}/{batch_id}/{uuid4()}_{file_name}"


def _worker_records():
    tenant_id = uuid4()
    batch_id = uuid4()
    resume_id = uuid4()
    storage_path = _storage_path(tenant_id, batch_id)
    batch = SimpleNamespace(
        id=batch_id,
        tenant_id=tenant_id,
        job_description="A sufficiently detailed job description.",
    )
    resume = SimpleNamespace(
        id=resume_id,
        batch_id=batch_id,
        tenant_id=tenant_id,
        storage_path=storage_path,
        file_name="resume.pdf",
        status="pending",
        ats_score=None,
    )
    tenant = SimpleNamespace(id=tenant_id)
    return tenant_id, batch_id, resume_id, storage_path, batch, resume, tenant


def test_resume_loader_rejects_resume_from_another_batch():
    tenant_id, batch_id, resume_id, storage_path, batch, resume, tenant = _worker_records()
    resume.batch_id = uuid4()
    session = FakeWorkerSession(batch=batch, resume=resume, tenant=tenant)

    with pytest.raises(ValueError, match="does not belong to the requested batch"):
        resume_task._load_verified_resume(
            session,
            batch_id=str(batch_id),
            resume_id=str(resume_id),
            storage_path=storage_path,
            file_name=resume.file_name,
            tenant_id=str(tenant_id),
        )


def test_resume_loader_rejects_message_path_and_filename_mismatch():
    tenant_id, batch_id, resume_id, storage_path, batch, resume, tenant = _worker_records()
    session = FakeWorkerSession(batch=batch, resume=resume, tenant=tenant)

    with pytest.raises(ValueError, match="storage path"):
        resume_task._load_verified_resume(
            session,
            batch_id=str(batch_id),
            resume_id=str(resume_id),
            storage_path="rf-bucket/another-tenant/another-batch/resume.pdf",
            file_name=resume.file_name,
            tenant_id=str(tenant_id),
        )

    with pytest.raises(ValueError, match="file name"):
        resume_task._load_verified_resume(
            session,
            batch_id=str(batch_id),
            resume_id=str(resume_id),
            storage_path=storage_path,
            file_name="different.pdf",
            tenant_id=str(tenant_id),
        )


def test_resume_loader_rejects_storage_path_outside_verified_prefix():
    tenant_id, batch_id, resume_id, _storage_path_value, batch, resume, tenant = _worker_records()
    resume.storage_path = f"{settings.S3_BUCKET}/{uuid4()}/{batch_id}/foreign.pdf"
    session = FakeWorkerSession(batch=batch, resume=resume, tenant=tenant)

    with pytest.raises(ValueError, match="tenant and batch"):
        resume_task._load_verified_resume(
            session,
            batch_id=str(batch_id),
            resume_id=str(resume_id),
            storage_path=resume.storage_path,
            file_name=resume.file_name,
            tenant_id=str(tenant_id),
        )


def test_batch_loader_rejects_task_tenant_mismatch():
    _tenant_id, batch_id, _resume_id, _storage_path_value, batch, resume, tenant = _worker_records()
    session = FakeWorkerSession(batch=batch, resume=resume, tenant=tenant)

    with pytest.raises(ValueError, match="does not own"):
        batch_task._load_verified_batch(session, str(batch_id), str(uuid4()))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "expected_status", "expected_reason"),
    [
        ("completed", "completed", None),
        ("processing", "skipped", "already_processing"),
    ],
)
async def test_duplicate_resume_delivery_is_idempotently_skipped(
    monkeypatch, status, expected_status, expected_reason
):
    tenant_id, batch_id, resume_id, storage_path, batch, resume, tenant = _worker_records()
    resume.status = status
    resume.ats_score = 91.0
    session = FakeWorkerSession(batch=batch, resume=resume, tenant=tenant)
    monkeypatch.setattr(resume_task, "Session", lambda _engine: session)

    result = await resume_task._process_resume_async(
        str(resume_id),
        storage_path,
        resume.file_name,
        batch_id=str(batch_id),
        tenant_id=str(tenant_id),
    )

    assert result["status"] == expected_status
    if expected_reason:
        assert result["reason"] == expected_reason
