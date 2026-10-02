<div align="center">

# 📄 ResumeFilter

**AI-powered resume screening and ATS scoring system**

[![Tests](https://github.com/your-username/resume-filter/actions/workflows/test.yml/badge.svg)](https://github.com/your-username/resume-filter/actions/workflows/test.yml)
[![Lint](https://github.com/your-username/resume-filter/actions/workflows/lint.yml/badge.svg)](https://github.com/your-username/resume-filter/actions/workflows/lint.yml)
[![Docker](https://github.com/your-username/resume-filter/actions/workflows/docker.yml/badge.svg)](https://github.com/your-username/resume-filter/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

[🇸🇦 العربية](README.ar.md) · [Architecture](docs/architecture.md) · [API Docs](docs/api.md)

</div>

---

## 🎯 What is ResumeFilter?

ResumeFilter is a production-grade, multi-tenant platform that helps
**organizations** screen resumes at scale and helps **individuals**
optimize their CVs for specific jobs.

It combines a **transparent 6-factor ATS engine** with a
**provider-agnostic LLM layer** (100+ AI providers via LiteLLM).

---

## ✨ Key Features

### For Organizations (B2B)
- 📦 **Batch processing** — Upload hundreds of resumes, get them scored in parallel.
- 🏢 **Multi-tenant** — Full data isolation via PostgreSQL Row-Level Security.
- 🔑 **Bring Your Own Key (BYOK)** — Connect OpenAI, Anthropic, Gemini, Groq, Azure, Bedrock, or a local Ollama.
- 📊 **Shortlist reports** — Ranked candidates with per-factor breakdown and evidence.
- 👥 **Role-based access** — Owner, admin, member, viewer.
- 🎛️ **Fallback to platform key** — Use the built-in provider or your own.

### For Individuals (B2C)
- 🎯 **Instant ATS score** against any job description.
- 🔍 **Keyword gap analysis** — See exactly what's missing.
- 💡 **Prioritized suggestions** — High/medium/low impact recommendations.
- 📜 **History** — Track your progress over time.
- 🆓 **Free tier** — 3 analyses per day.

### Engineering Highlights
- ⚡ **Async-first** — FastAPI + asyncpg + httpx throughout.
- 🔀 **Celery + Chord** — Fan-out/fan-in for batch processing.
- 🛡️ **Defense in depth** — JWT + Fernet encryption + RLS + BCrypt.
- 📈 **Structured logging** — JSON logs with request IDs for tracing.
- 🐳 **Docker-ready** — Multi-stage builds, ~200 MB images.
- ☸️ **Kubernetes-ready** — KEDA autoscaling manifests included.
- 🧪 **Tested** — Pytest + coverage + Ruff + Mypy in CI.

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│ NiceGUI Frontend (/ui) │
└──────────────────────────┬──────────────────────────────────┘
│
┌──────────────────────────▼──────────────────────────────────┐
│ FastAPI Backend (/api/v1) │
│ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐ │
│ │ Auth │ │ B2C │ │ B2B │ │ Settings │ │
│ └──────────┘ └──────────┘ └───────────┘ └────────────┘ │
└────┬─────────────┬──────────────┬──────────────┬────────────┘
│ │ │ │
▼ ▼ ▼ ▼
┌─────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────┐
│Postgres │ │ Redis │ │ MinIO │ │ Celery Worker │
│ + RLS │ │ + Queue │ │ (Files) │ │ (Parallel) │
└─────────┘ └──────────┘ └───────────┘ └───────┬───────┘
│
▼
┌───────────────────┐
│ LiteLLM (100+) │
│ Groq, OpenAI, ... │
└───────────────────┘

text

See [docs/architecture.md](docs/architecture.md) for details.

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (with Compose v2)
- Python 3.12+ (for local development)

### 1. Clone & configure

```bash
git clone https://github.com/your-username/resume-filter.git
cd resume-filter
cp .env.example .env
python scripts/generate_master_key.py
Copy the generated values into .env (SECRET_KEY, MASTER_KEY).

2. Get a free Groq API key
Sign up at console.groq.com and paste it:

env
PLATFORM_LLM_API_KEY=gsk_xxxxxxxxxxxx
3. Launch everything
bash
docker-compose -f docker/docker-compose.yml up -d --build
4. Open in your browser
Service	URL
Web UI	http://localhost:8000/ui
API Docs	http://localhost:8000/docs
Celery Flower	http://localhost:5555
MinIO Console	http://localhost:9001
Default MinIO credentials: minioadmin / minioadmin.

📁 Project Structure
text
resume-filter/
├── app/                    # FastAPI backend
│   ├── api/v1/             # REST endpoints
│   ├── core/               # Config, security, logging, middleware
│   ├── db/                 # SQLAlchemy models + RLS sessions
│   ├── providers/          # LLM abstraction (LiteLLM)
│   ├── services/           # Business logic (ATS, parsing, storage)
│   ├── workers/            # Celery tasks
│   └── schemas/            # Pydantic models
├── ui/                     # NiceGUI frontend
│   ├── components/         # Reusable UI pieces
│   └── pages/              # Route handlers
├── docker/                 # Dockerfiles + Compose
├── k8s/                    # Kubernetes manifests
├── alembic/                # Database migrations
├── tests/                  # Pytest suite
├── scripts/                # Utility scripts
└── docs/                   # Architecture + API docs
🧪 Testing
bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=app

# Lint & type-check
ruff check app ui tests
mypy app ui
🛠️ Tech Stack
Layer	Technology
Backend	FastAPI 0.115, Python 3.12
Database	PostgreSQL 16 (with Row-Level Security)
ORM	SQLAlchemy 2.0 (async) + Alembic
Task Queue	Celery 5.4 + Redis 7
Object Storage	MinIO (S3-compatible)
LLM Abstraction	LiteLLM (100+ providers)
Auth	JWT (python-jose) + BCrypt
Encryption	Fernet (cryptography)
Frontend	NiceGUI 2.9 (Python-only)
Logging	structlog (JSON in production)
Testing	pytest + coverage
Linting	Ruff + Mypy
CI/CD	GitHub Actions
Containers	Docker + Docker Compose
Orchestration	Kubernetes + KEDA
🔒 Security
Multi-tenant isolation — PostgreSQL RLS + per-request tenant context.

API keys encrypted — Fernet-encrypted before storage.

Passwords hashed — BCrypt via passlib.

JWT-based auth — Short-lived tokens, signed with SECRET_KEY.

Prompt injection defense — System prompts enforce strict roles.

Row-level policies — Two-layer defense (ORM filter + DB policy).

Report vulnerabilities privately — see SECURITY.md.

📖 Documentation
Architecture

API Reference

Contributing Guide

Changelog

🤝 Contributing
Contributions are welcome! Please read CONTRIBUTING.md.

📄 License
MIT — see LICENSE.

<div align="center">
Built with ❤️ using Python, FastAPI, and NiceGUI.

</div> ```