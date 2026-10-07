# ResumeFilter Full Audit

## Scope

Audited the repository's runtime architecture, API, UI, database, security, worker queue, deployment, and tests with the code as source of truth.

## Baseline validation

- `python -m pytest tests -q` on Python 3.11.9: **29 passed**
- `compileall -q app ui alembic scripts`: **passed**
- `ruff check app ui tests scripts`: **passed**
- `ruff format --check app ui tests scripts`: **passed**

## Verified findings

1. B2C quota setting was missing from `app/core/config.py`, which caused `app/api/v1/b2c/analyze.py` to raise `AttributeError` at runtime.
2. B2B resume comparison routes in `app/api/v1/b2b/results.py` were shadowed by the dynamic `/{resume_id}` route.
3. B2B tenant access did not check `Tenant.is_active` in `app/core/dependencies.py`.
4. B2B admin-like settings routes lacked role checks.
5. Batch upload failed open on file naming/content safety and did not clean up uploaded objects on failure.
6. The RLS migration granted a runtime role bypass policy, undermining tenant isolation.
7. The API entrypoint suppressed Alembic migration failures.
8. Kubernetes configuration used mismatched storage/database variables and an invalid API command.
9. CI security and lint workflows treated important checks as non-blocking.
10. Test coverage was narrow: only ATS and keyword-matching logic had unit tests.

## Fixes applied

- Added `B2C_DAILY_LIMIT` to application settings.
- Constrained B2B resume routes to UUID paths.
- Enforced tenant activity checks in B2B user resolution.
- Added role-gated helpers for tenant and batch operations.
- Hardened B2B batch upload validation and rollback cleanup.
- Removed the RLS bypass policy from migration 0002.
- Made the API entrypoint fail when migrations fail.
- Replaced the Kubernetes API command with installed `uvicorn`.
- Normalized Kubernetes storage variables to `S3_*` and documented a valid `DATABASE_URL`.
- Removed non-blocking security/lint exception behavior.

## Notes

- The repository still has a limited automated test surface outside ATS and keyword matching.
- Some higher-level integration behaviors remain untested because they require database, Redis, and storage services.
