# API Reference

Base URL: `http://localhost:8000/api/v1`

All request/response bodies are JSON unless noted.
Authentication is via **Bearer JWT** in the `Authorization` header.

---

## Authentication

### Register (B2C — individuals)

```http
POST /api/v1/auth/register/b2c
Content-Type: application/json

{
  "email": "jane@example.com",
  "password": "supersecret",
  "account_type": "b2c"
}
Response 201

json
{ "access_token": "eyJ...", "token_type": "bearer" }
Register (B2B — organizations)
http
POST /api/v1/auth/register/b2b
Content-Type: application/json

{
  "organization_name": "Acme Corp",
  "organization_slug": "acme-corp",
  "email": "owner@acme.com",
  "password": "supersecret"
}
Response 201

json
{ "access_token": "eyJ...", "token_type": "bearer" }
Login
http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=jane@example.com&password=supersecret
Response 200

json
{ "access_token": "eyJ...", "token_type": "bearer" }
Current user
http
GET /api/v1/auth/me
Authorization: Bearer <token>
Response 200

json
{
  "id": "uuid",
  "email": "jane@example.com",
  "is_active": true,
  "is_verified": false,
  "role": "member",
  "account_type": "b2c",
  "tenant_id": null
}
B2C — Individuals
Analyze a resume
http
POST /api/v1/b2c/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_text": "John Doe\nSenior Python Developer...",
  "job_description": "We are hiring a Python backend engineer..."
}
Response 200

json
{
  "id": "uuid",
  "ats_score": 82.4,
  "level": "good",
  "level_label": "Good",
  "breakdown": {
    "keyword_match": 71.4,
    "action_verbs": 85.0,
    "quantified_achievements": 70.0,
    "section_completeness": 100.0,
    "contact_info": 100.0,
    "length_and_clarity": 100.0
  },
  "matched_keywords": ["python", "fastapi", "postgresql"],
  "missing_keywords": ["kubernetes", "celery"],
  "suggestions": [
    {
      "type": "add_keyword",
      "priority": "high",
      "description": "Add 'Kubernetes' if you have experience with it."
    }
  ],
  "created_at": "2026-10-02T12:00:00Z"
}
Errors

Code	Meaning
400	Validation error
401	Missing or invalid token
403	Not a B2C account
429	Daily limit reached (3/day)
502	LLM provider error
Analysis history
http
GET /api/v1/b2c/history?limit=20
Authorization: Bearer <token>
Response 200

json
[
  {
    "id": "uuid",
    "ats_score": 82.4,
    "breakdown": { ... },
    "missing_keywords": ["kubernetes"],
    "created_at": "2026-10-02T12:00:00Z"
  }
]
B2B — Organizations
All B2B endpoints require a b2b account. Row-Level Security
automatically scopes results to the caller's tenant.

Create a batch
http
POST /api/v1/b2b/batches
Authorization: Bearer <token>
Content-Type: multipart/form-data

job_title=Senior Python Developer
job_description=We are hiring...
job_requirements=5+ years experience (optional)
files=<file1.pdf>
files=<file2.docx>
Response 201

json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "job_title": "Senior Python Developer",
  "status": "pending",
  "total_resumes": 2,
  "completed": 0,
  "failed": 0,
  "created_at": "2026-10-02T12:00:00Z",
  "completed_at": null
}
Limits

Max 500 files per batch.

Max 10 MB per file.

Accepted formats: .pdf, .docx.

Get batch status
http
GET /api/v1/b2b/batches/{batch_id}
Authorization: Bearer <token>
Response 200

json
{
  "id": "uuid",
  "job_title": "Senior Python Developer",
  "status": "processing",
  "total_resumes": 100,
  "completed": 47,
  "failed": 3
}
List batch resumes
http
GET /api/v1/b2b/batches/{batch_id}/resumes
Authorization: Bearer <token>
Response 200

json
[
  {
    "id": "uuid",
    "file_name": "cv_john.pdf",
    "candidate_name": "John Doe",
    "candidate_email": "john@example.com",
    "ats_score": 87.5,
    "status": "completed",
    "missing_keywords": ["kubernetes"],
    "suggestions": [ ... ],
    "created_at": "2026-10-02T12:00:00Z"
  }
]
Results are sorted by ats_score descending (nulls last).

Full resume report
http
GET /api/v1/b2b/resumes/{resume_id}
Authorization: Bearer <token>
Response 200

json
{
  "id": "uuid",
  "file_name": "cv_john.pdf",
  "candidate_name": "John Doe",
  "candidate_email": "john@example.com",
  "candidate_phone": "+970 599 123 456",
  "ats_score": 87.5,
  "score_breakdown": { ... },
  "missing_keywords": ["kubernetes"],
  "suggestions": [ ... ],
  "status": "completed",
  "error_message": null,
  "created_at": "2026-10-02T12:00:00Z"
}
B2B — LLM Settings (BYOK)
Get current settings
http
GET /api/v1/b2b/settings/llm
Authorization: Bearer <token>
Response 200

json
{
  "provider": "groq",
  "model": "groq/llama-3.1-8b-instant",
  "has_custom_key": false,
  "base_url": null,
  "source": "platform"
}
source is either "platform" (using the shared key) or "tenant"
(using the tenant's own key).

Update settings
http
PUT /api/v1/b2b/settings/llm
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "anthropic",
  "model": "anthropic/claude-sonnet-4-20250514",
  "api_key": "sk-ant-...",
  "base_url": null
}
Response 200 — same shape as GET.

The API key is encrypted with Fernet before storage.

Delete custom key
http
DELETE /api/v1/b2b/settings/llm
Authorization: Bearer <token>
Response 204 — No content.

Reverts the tenant to the platform default.

List supported providers
http
GET /api/v1/b2b/settings/llm/providers
Authorization: Bearer <token>
Response 200

json
{
  "providers": [
    {
      "provider": "groq",
      "models": ["groq/llama-3.3-70b-versatile", "..."],
      "requires_api_key": true,
      "supports_base_url": false
    }
  ],
  "platform_default": {
    "provider": "groq",
    "model": "groq/llama-3.1-8b-instant"
  }
}
Test connection
http
POST /api/v1/b2b/settings/llm/test
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "openai",
  "model": "openai/gpt-4o-mini",
  "api_key": "sk-...",
  "base_url": null
}
Response 200

json
{
  "success": true,
  "message": "Connection successful.",
  "latency_ms": 342
}
Error Format
All errors follow a consistent shape:

json
{
  "error": "limit_exceeded",
  "message": "Daily limit reached (3 analyses/day). Try again tomorrow.",
  "request_id": "abc-123"
}
For validation errors (422), an additional details.errors array
contains the field-level issues from Pydantic.

Health & Meta
Health check
http
GET /health
Response 200

json
{ "status": "ok", "app": "ResumeFilter", "env": "development" }
OpenAPI spec
Format	URL
Swagger UI	/docs
ReDoc	/redoc
Raw JSON	/openapi.json
Rate Limits
Endpoint	Limit
POST /b2c/analyze	3 / day / user
POST /b2b/batches	By tenant plan
POST /auth/login	Not enforced (add via ingress)
When exceeded, the API returns 429 Too Many Requests with
error: "limit_exceeded".