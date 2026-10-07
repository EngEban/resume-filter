# Stabilization Report

## Docker verification results

The Docker stack was built and started with:

```text
docker compose -f docker/docker-compose.yml up -d --build
```

Running services:

- PostgreSQL 16 — healthy
- Redis 7 — healthy
- SeaweedFS — running
- API — running
- Celery worker — running and responding to `inspect ping`
- Flower — running
- Migration job — completed successfully on a clean database

Verified inside Docker:

- `python -m compileall -q app ui alembic scripts` — passed
- `GET /health` — HTTP 200
- `GET /api/v1/health/full` — healthy; database, Redis, storage, and LLM checks passed
- API OpenAPI contains `/api/v1/b2b/resumes/compare` and `/api/v1/b2b/resumes/compare/export.xlsx`
- Celery worker `inspect ping` — one worker online
- Runtime database migration revision — `0003_llm_settings`
- RLS under `rf_app` — runtime role reported `rolsuper=false`, `rolbypassrls=false`; each tenant saw only its own batch
- B2C registration through the running API — HTTP 201

The complete requested test/lint command could not finish inside Docker because the production image does not include development tools and Docker DNS failed while installing `requirements-dev.txt` from PyPI. Therefore pytest, coverage, Ruff, and mypy are **not claimed as Docker-verified** in this pass.

## Applied stabilization changes

- Added missing B2C daily limit configuration.
- Prevented `/b2b/resumes/compare` route shadowing.
- Enforced tenant active-state checks.
- Added role-gated helpers for B2B operations.
- Hardened batch upload validation and failure cleanup.
- Removed runtime RLS bypass policy from migration 0002.
- Made Alembic failures fail the API entrypoint.
- Fixed Kubernetes config variable mismatches and the API launch command.
- Made lint and security workflows fail on important issues.
- Added Docker migration ordering and a restricted non-superuser runtime role.
- Added the Compose migration job and made API/worker depend on its successful completion.
- Added first-boot creation of the restricted application database role.
- Corrected the PostgreSQL Compose healthcheck to use the restricted application role instead of assuming the host-side database user.

## Remaining risks

- Docker validation could not install `requirements-dev.txt` because PyPI name resolution failed inside the disposable validation container.
- The current persistent development volume was created before migration tracking existed; it required an explicit one-time `alembic stamp head` after confirming its schema matched the migrations. A fresh volume should run migrations normally.
- The full batch upload/LLM processing path was not run with a real resume and external LLM call.
- Flower emitted inspect warnings for some control commands despite the worker being reachable by ping.
- The Docker production images intentionally contain runtime dependencies only; a repeatable test image/service should be added before CI or local Docker test execution is required.

## Files modified during the Docker verification pass

- `docker/docker-compose.yml`
- `docs/stabilization_report.md`
