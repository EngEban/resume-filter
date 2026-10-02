# Architecture

ResumeFilter is a multi-tenant, asynchronous, event-driven platform for
resume screening and ATS scoring. This document describes its structure,
data flow, and key design decisions.

---

## 1. High-Level Diagram
┌─────────────────────────────────────────────────────────────────┐
│ Client (Browser) │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │ NiceGUI Frontend → /ui │ │
│ │ Swagger UI → /docs │ │
│ └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
│ HTTP/JSON, JWT
┌─────────────────────────────▼───────────────────────────────────┐
│ FastAPI Application │
│ │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐ │
│ │ Auth │ │ B2C │ │ B2B │ │ Settings │ │
│ │ /auth/* │ │ /b2c/* │ │ /b2b/* │ │ /b2b/set* │ │
│ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └──────┬──────┘ │
│ │ │ │ │ │
│ └──────────────┴──────────────┴────────────────┘ │
│ │ │
│ ┌────────▼────────┐ │
│ │ Services │ │
│ │ ATS Engine │ │
│ │ Parser │ │
│ │ Feedback │ │
│ │ Storage │ │
│ │ Limits │ │
│ └────────┬────────┘ │
└───────────────────────┼─────────────────────────────────────────┘
│
┌────────────────┼───────────────────┐
▼ ▼ ▼
┌────────────┐ ┌────────────┐ ┌────────────────┐
│ PostgreSQL │ │ Redis │ │ MinIO │
│ + RLS │ │ Broker + │ │ (S3-compat) │
│ │ │ Cache │ │ │
└────────────┘ └─────┬──────┘ └────────────────┘
│
┌──────▼───────┐
│ Celery │
│ Workers │
└──────┬───────┘
│
▼
┌────────────────────┐
│ LiteLLM (100+) │
│ Groq, OpenAI, ... │
└────────────────────┘

text

---

## 2. Data Flow

### 2.1 B2C Analysis (synchronous)
User → POST /api/v1/b2c/analyze
→ check daily limit (Redis/Postgres)
→ parse resume (regex, in-process)
→ call LLM (async via LiteLLM)
→ calculate ATS score
→ persist Analysis row
→ return JSON

text

**Latency**: 5–15 seconds (dominated by the LLM call).

### 2.2 B2B Batch (asynchronous, fan-out/fan-in)
User → POST /api/v1/b2b/batches (multipart upload)
→ create Batch row
→ upload each file to MinIO
→ create Resume rows
→ Celery: process_batch.delay(batch_id)
→ return { batch_id, status: "pending" } ← immediate

Celery Worker #1: process_batch
→ load resumes
→ build chord(group(process_resume) | finalize_batch)
→ dispatch to queue

Celery Worker #N: process_resume (parallel, one per resume)
→ download from MinIO
→ extract text (pdfplumber / python-docx / OCR)
→ parse + LLM analysis
→ calculate ATS score
→ persist result
→ return

Celery Worker #1: finalize_batch
→ aggregate counts
→ update Batch status

text

**Why a chord?** It gives us a barrier: `finalize_batch` runs only
after every `process_resume` task finishes (success or failure).

---

## 3. Multi-Tenancy

### 3.1 Model

Every tenant-scoped table (`users`, `batches`, `resumes`) carries a
`tenant_id` column. Two layers of isolation apply:

1. **Application layer** — Every query filters by `tenant_id` from the JWT.
2. **Database layer** — PostgreSQL Row-Level Security (RLS) enforces it
   even if the application forgets.

### 3.2 RLS Mechanism

```sql
-- On every request with a tenant context:
SET LOCAL app.current_tenant = '<uuid>';

-- Policy on the table:
CREATE POLICY tenant_isolation_users ON users
    USING (tenant_id = current_setting('app.current_tenant')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid);
SET LOCAL is transaction-scoped, so it does not leak between
requests that reuse the same connection.

3.3 The get_tenant_db Dependency
python
async def get_tenant_db(user = Depends(get_current_b2b_user)):
    assert user.tenant_id is not None
    async with get_session(user.tenant_id) as session:
        yield session
Use this dependency in any B2B endpoint instead of get_db.

4. LLM Provider Abstraction
4.1 Why LiteLLM?
LiteLLM provides a single async API (acompletion) that talks to
100+ providers. It normalizes request and response shapes, handles
retries, and tracks token usage.

4.2 Resolution Order
text
resolve_llm_config(tenant)
    │
    ├── tenant.llm_api_key_encrypted present?
    │       → decrypt → use tenant's provider
    │
    └── otherwise
            → use platform default (settings.PLATFORM_LLM_*)
4.3 Model Naming
Always use the <provider>/<model> format:

text
groq/llama-3.1-8b-instant
openai/gpt-4o-mini
anthropic/claude-sonnet-4-20250514
gemini/gemini-1.5-flash
ollama/llama3.1:8b
4.4 Security
Keys are encrypted with Fernet using MASTER_KEY.

Decryption happens only inside the worker or request that needs it.

Decrypted keys are never logged and never serialized to the client.

5. ATS Engine
5.1 Factors and Weights
Factor	Weight	Source
Keyword match	35%	Deterministic (regex + tokenization)
Action verbs	15%	LLM (0–100)
Quantified achievements	15%	LLM (0–100)
Section completeness	15%	Deterministic
Contact info	10%	Deterministic
Length & clarity	10%	Deterministic
Total = weighted sum, rounded to 2 decimals.

5.2 Levels
Score	Level
90–100	excellent
75–89	good
60–74	average
40–59	below_average
0–39	weak
5.3 Why Keyword Match Dominates?
Industry research shows that real ATS systems weight keyword matching
at 70–80% of the final decision. We compromise at 35% because we also
evaluate subjective qualities that matter to human reviewers.

6. Async Strategy
FastAPI endpoints are async def.

SQLAlchemy uses asyncpg (via create_async_engine).

httpx is used for outbound HTTP (UI → API, LiteLLM internals).

Celery tasks are synchronous, but each task wraps an
asyncio.run(...) call for the async pipeline inside.

Why? Celery's execution model is process-based and does not play well
with a persistent event loop across prefork workers. Isolating the
async pipeline per task is safe and simple.

7. Storage Layout
MinIO objects follow this key convention:

text
<bucket>/
  <tenant_id>/
    <batch_id>/
      <resume_uuid>_<original_filename>
This makes bulk deletion per tenant or per batch trivial, and it keeps
objects logically separated even without RLS (MinIO is not multi-tenant
by itself).

8. Failure Handling
Failure	Behavior
LLM provider down	Retry (2× in LiteLLM) → fallback to platform key → mark resume failed
MinIO unreachable	Resume task fails, retried with backoff
Worker crash mid-task	task_acks_late → task re-delivered
Batch partially fails	finalize_batch still runs via chord
DB transaction error	Session rolls back, exception handler returns 500
Invalid JWT	401 with WWW-Authenticate header
9. Logging and Observability
Structured logging via structlog.

JSON in production, colorized in development.

Every request gets a request_id (UUIDv4, or X-Request-ID
header if the client supplies one).

Response headers include X-Request-ID and X-Process-Time-Ms.

Celery Flower provides task-level dashboards.

10. Configuration
All configuration is externalized via .env. See .env.example for
the full list. In production, use environment variables from your
orchestrator (Kubernetes Secrets, Docker secrets, etc.).

Never commit .env to version control.

11. Extension Points
Feature	Where to add
New LLM provider	Nothing to do — LiteLLM supports it. Just pick the model name.
New scoring factor	app/services/ats_engine.py + WEIGHTS
New API endpoint	app/api/v1/<area>/<file>.py + register in router.py
New background task	app/workers/tasks/<file>.py + add to celery_app.include
New UI page	ui/pages/<file>.py + register in ui/main.py
New migration	alembic revision --autogenerate -m "..."
12. Non-Goals
To keep the scope focused, this project does not:

Serve as a full ATS (no interview scheduling, no offer letters).

Provide real-time chat with the LLM.

Store raw resume text in logs.

Support non-HTTP transports (no gRPC, no message bus consumers).

Implement fine-grained per-user permissions beyond roles.