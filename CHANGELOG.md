# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-provider LLM support via LiteLLM (Groq, OpenAI, Anthropic, Gemini, Azure, Bedrock, Ollama).
- Bring Your Own Key (BYOK) per tenant with Fernet encryption.
- Platform default LLM key with strict per-user quotas.
- Transparent 6-factor ATS scoring engine.
- B2C single-resume analysis endpoint with suggestion generation.
- B2B batch upload with Celery fan-out/fan-in processing.
- NiceGUI frontend (landing, login, register, dashboard, B2C, B2B).
- PostgreSQL Row-Level Security for multi-tenant isolation.
- Structured logging with request IDs.
- Global exception handlers with unified error schema.
- Alembic migrations (initial schema + RLS + LLM settings).
- Docker Compose stack (PostgreSQL, Redis, MinIO, API, Worker, Flower).
- GitHub Actions workflows (test, lint, docker, security).
- Pytest suite for ATS engine and keyword matcher.
- Ruff + Mypy + Pyproject configuration.

### Security
- Fernet encryption for tenant API keys.
- BCrypt password hashing.
- JWT with short-lived access tokens.
- Non-root Docker containers.

## [0.1.0] - 2026-10-02

### Added
- Initial project scaffolding.
- Repository structure and tooling.