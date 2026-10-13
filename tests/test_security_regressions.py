from datetime import UTC, datetime, timedelta
from io import BytesIO
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile
from jose import jwt

from app.api.v1.b2b import analytics as analytics_module
from app.api.v1.b2b import batches as batches_module
from app.api.v1.b2b import results as results_module
from app.api.v1.b2b.authorization import get_tenant_batch, get_tenant_resume
from app.api.v1.b2b.results import router as results_router
from app.core import dependencies
from app.core.config import settings as app_settings
from app.core.exceptions import LimitExceededError
from app.services.limits import check_b2c_daily_limit
from app.workers.tasks import resume as resume_task


class FakeDb:
    def __init__(self, tenant=None, scalar=0):
        self.tenant = tenant
        self.scalar = scalar
        self.added = []
        self.committed = False

    async def get(self, _model, _tenant_id):
        return self.tenant

    def add(self, value):
        self.added.append(value)

    async def flush(self):
        return None

    async def commit(self):
        self.committed = True

    async def refresh(self, _value):
        return None

    async def execute(self, _statement):
        return SimpleNamespace(scalar_one=lambda: self.scalar)


class CapturingDb:
    """Capture generated SQL while returning no cross-tenant rows."""

    def __init__(self):
        self.statement = None

    async def execute(self, statement):
        self.statement = statement
        return SimpleNamespace(
            scalar_one_or_none=lambda: None,
            scalars=lambda: SimpleNamespace(all=lambda: []),
        )


@pytest.mark.asyncio
async def test_inactive_tenant_is_rejected():
    user = SimpleNamespace(account_type="b2b", tenant_id=uuid4())
    db = FakeDb(tenant=SimpleNamespace(is_active=False))

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_b2b_user(user, db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_tenant_db_uses_authenticated_tenant_scope(monkeypatch):
    captured = {}

    class Context:
        async def __aenter__(self):
            return "scoped-session"

        async def __aexit__(self, *_args):
            return False

    def fake_get_session(tenant_id):
        captured["tenant_id"] = tenant_id
        return Context()

    monkeypatch.setattr(dependencies, "get_session", fake_get_session)
    tenant_id = uuid4()
    user = SimpleNamespace(tenant_id=tenant_id)
    generator = dependencies.get_tenant_db(user)
    assert await anext(generator) == "scoped-session"
    await generator.aclose()

    assert captured["tenant_id"] == tenant_id


@pytest.mark.asyncio
async def test_batch_list_query_is_scoped_to_authenticated_tenant():
    db = CapturingDb()
    user = SimpleNamespace(tenant_id=uuid4(), role="member")

    assert await batches_module.list_batches(user, db) == []
    assert "batches.tenant_id" in str(db.statement)


@pytest.mark.asyncio
async def test_foreign_batch_is_rejected_by_ownership_helper():
    db = CapturingDb()

    with pytest.raises(HTTPException) as exc_info:
        await get_tenant_batch(db, uuid4(), uuid4())

    assert exc_info.value.status_code == 404
    statement = str(db.statement)
    assert "batches.tenant_id" in statement
    assert "batches.id" in statement


@pytest.mark.asyncio
async def test_foreign_resume_requires_owned_resume_and_batch():
    db = CapturingDb()

    with pytest.raises(HTTPException) as exc_info:
        await get_tenant_resume(db, uuid4(), uuid4())

    assert exc_info.value.status_code == 404
    statement = str(db.statement)
    assert "resumes.tenant_id" in statement
    assert "batches.tenant_id" in statement
    assert "resumes.id" in statement


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    [
        batches_module.get_batch,
        batches_module.list_batch_resumes,
        batches_module.export_batch_xlsx,
        batches_module.export_batch_pdf,
        batches_module.reprocess_batch,
        analytics_module.batch_analytics,
        results_module.compare_candidates,
        results_module.export_comparison_xlsx,
    ],
)
async def test_batch_scoped_endpoints_reject_a_foreign_batch(endpoint):
    db = CapturingDb()
    user = SimpleNamespace(tenant_id=uuid4(), role="member")
    batch_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        if endpoint in {
            results_module.compare_candidates,
            results_module.export_comparison_xlsx,
        }:
            await endpoint(user, db, batch_id)
        else:
            await endpoint(batch_id, user, db)

    assert exc_info.value.status_code == 404
    assert "batches.tenant_id" in str(db.statement)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    [results_module.get_resume_report, results_module.export_resume_pdf],
)
async def test_resume_scoped_endpoints_reject_a_foreign_resume(endpoint):
    db = CapturingDb()
    user = SimpleNamespace(tenant_id=uuid4(), role="member")

    with pytest.raises(HTTPException) as exc_info:
        await endpoint(uuid4(), user, db)

    assert exc_info.value.status_code == 404
    assert "resumes.tenant_id" in str(db.statement)


@pytest.mark.asyncio
async def test_tenant_overview_query_is_scoped_to_authenticated_tenant():
    db = CapturingDb()
    user = SimpleNamespace(tenant_id=uuid4(), role="member")

    overview = await analytics_module.tenant_overview(user, db)

    assert overview.total_batches == 0
    assert "batches.tenant_id" in str(db.statement)


@pytest.mark.asyncio
async def test_role_restricted_operations_reject_member():
    user = SimpleNamespace(role="member")

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.require_tenant_admin(user)

    assert exc_info.value.status_code == 403


def test_comparison_routes_are_not_shadowed():
    routes = {route.path: route.endpoint.__name__ for route in results_router.routes}

    assert routes["/b2b/resumes/compare"] == "compare_candidates"
    assert routes["/b2b/resumes/compare/export.xlsx"] == "export_comparison_xlsx"
    assert "/b2b/resumes/{resume_id:uuid}" in routes


@pytest.mark.asyncio
async def test_batch_upload_rejects_invalid_file_and_cleans_previous_upload(monkeypatch):
    uploaded = []
    deleted = []

    def fake_upload_file(**kwargs):
        path = f"resumes/{kwargs['object_name']}"
        uploaded.append(path)
        return path

    monkeypatch.setattr(batches_module, "upload_file", fake_upload_file)
    monkeypatch.setattr(batches_module, "delete_file", deleted.append)
    monkeypatch.setattr(
        batches_module.process_batch,
        "delay",
        lambda _batch_id, **_kwargs: None,
    )

    user = SimpleNamespace(tenant_id=uuid4(), role="member")
    db = FakeDb()
    valid = UploadFile(filename="candidate.pdf", file=BytesIO(b"pdf"))
    invalid = UploadFile(filename="malicious.exe", file=BytesIO(b"exe"))

    with pytest.raises(HTTPException) as exc_info:
        await batches_module.create_batch(
            user, db, "Engineer", "A job description", None, [valid, invalid]
        )

    assert exc_info.value.status_code == 400
    assert uploaded
    assert deleted == uploaded
    assert not db.committed


@pytest.mark.asyncio
async def test_batch_upload_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr(
        batches_module, "upload_file", lambda **_kwargs: pytest.fail("must not upload")
    )
    user = SimpleNamespace(tenant_id=uuid4(), role="member")
    db = FakeDb()
    oversized = UploadFile(
        filename="large.pdf",
        file=BytesIO(b"x" * (app_settings.B2B_MAX_FILE_SIZE_MB * 1024 * 1024 + 1)),
    )

    with pytest.raises(HTTPException) as exc_info:
        await batches_module.create_batch(
            user, db, "Engineer", "A job description", None, [oversized]
        )

    assert exc_info.value.status_code == 413


@pytest.mark.asyncio
async def test_b2c_daily_limit_is_enforced():
    db = FakeDb(scalar=app_settings.B2C_DAILY_LIMIT)

    with pytest.raises(LimitExceededError) as exc_info:
        await check_b2c_daily_limit(uuid4(), db, limit=app_settings.B2C_DAILY_LIMIT)

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_invalid_and_expired_tokens_are_rejected(monkeypatch):
    db = FakeDb()

    with pytest.raises(HTTPException) as invalid:
        await dependencies.get_current_user("not-a-token", db)
    assert invalid.value.status_code == 401

    expired = jwt.encode(
        {"sub": str(uuid4()), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        app_settings.SECRET_KEY,
        algorithm=dependencies.ALGORITHM,
    )
    with pytest.raises(HTTPException) as expired_exc:
        await dependencies.get_current_user(expired, db)
    assert expired_exc.value.status_code == 401


def test_retry_exhaustion_returns_terminal_failure(monkeypatch):
    async def fail_processing(*_args, **_kwargs):
        raise RuntimeError("provider failed")

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def get(self, _model, _resume_id):
            return SimpleNamespace(status="pending", error_message=None)

        def commit(self):
            return None

    monkeypatch.setattr(resume_task, "_process_resume_async", fail_processing)
    monkeypatch.setattr(resume_task, "Session", lambda _engine: FakeSession())

    resume_task.process_resume.push_request(retries=resume_task.process_resume.max_retries)
    try:
        result = resume_task.process_resume.run("batch", str(uuid4()), "resumes/file", "file.pdf")
    finally:
        resume_task.process_resume.pop_request()

    assert result["status"] == "failed"
    assert result["error"] == "provider failed"
