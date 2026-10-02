#!/bin/bash
# ============================================================
# docker/entrypoint-api.sh
# Entrypoint for the FastAPI container.
# ============================================================
set -e

echo "Waiting for PostgreSQL..."
python scripts/wait_for_db.py

echo "Running Alembic migrations..."
alembic upgrade head || echo "Alembic upgrade skipped (no migrations yet)."

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000