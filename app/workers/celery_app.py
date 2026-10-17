# ============================================================
# app/workers/celery_app.py
# Celery Application with persistent event loop per worker.
# ============================================================
import asyncio
import logging

from celery import Celery
from celery.signals import worker_process_init

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------- Celery App ----------
celery_app = Celery(
    "resume_filter",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.batch",
        "app.workers.tasks.resume",
    ],
)


# ---------- Configuration ----------
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    result_expires=86400,
    broker_transport_options={
        "visibility_timeout": 43200,
        "max_retries": 3,
    },
    result_backend_transport_options={
        "visibility_timeout": 43200,
    },
    task_default_queue="default",
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "high_priority": {"exchange": "high_priority", "routing_key": "high_priority"},
        "low_priority": {"exchange": "low_priority", "routing_key": "low_priority"},
    },
)


# ============================================================
# Persistent Event Loop per Worker Process
# ============================================================
# Celery uses a prefork pool: each worker process handles
# multiple tasks. asyncio.run() creates AND closes a loop per
# task, invalidating global HTTP clients cached by litellm.
#
# Solution: create ONE persistent event loop per worker process
# at fork time. Never close it. Tasks reuse the same loop via
# `loop.run_until_complete()`.
# ============================================================
@worker_process_init.connect
def init_worker_process(**kwargs) -> None:
    """Runs in each forked worker process after fork."""
    # Create and register a persistent event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Silence verbose third-party logs
    import litellm

    litellm.suppress_debug_info = True
    litellm.set_verbose = False
    litellm.drop_params = True

    logger.info("Worker process initialized (persistent event loop ready).")
