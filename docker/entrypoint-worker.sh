#!/bin/bash
# ============================================================
# docker/entrypoint-worker.sh
# Entrypoint for the Celery worker container.
# ============================================================
set -e

echo "Waiting for PostgreSQL..."
python scripts/wait_for_db.py

echo "Starting Celery worker..."
exec celery -A app.workers.celery_app worker \
    --loglevel=info \
    --concurrency=${CELERY_CONCURRENCY:-4} \
    --max-tasks-per-child=1000