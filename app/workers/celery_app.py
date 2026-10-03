# ============================================================
# app/workers/celery_app.py
# Celery Application Configuration
# ============================================================
from celery import Celery

from app.core.config import settings

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
    # ---------- Serialization ----------
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # ---------- Timezone ----------
    timezone="UTC",
    enable_utc=True,
    # ---------- Task Limits ----------
    task_time_limit=600,  # 10 دقائق (قتل قسري)
    task_soft_time_limit=540,  # 9 دقائق (SoftTimeLimitExceeded)
    # ---------- Worker Behavior ----------
    worker_prefetch_multiplier=1,  # توزيع عادل
    worker_max_tasks_per_child=1000,  # إعادة تشغيل Worker بعد 1000 مهمة
    worker_disable_rate_limits=False,
    # ---------- Reliability ----------
    task_acks_late=True,  # ACK بعد الانتهاء (لا تفقد المهام)
    task_reject_on_worker_lost=True,  # إعادة المهمة إذا مات الـ Worker
    task_track_started=True,
    # ---------- Results ----------
    result_expires=86400,  # 24 ساعة
    # ---------- Redis Transport ----------
    broker_transport_options={
        "visibility_timeout": 43200,  # 12 ساعة
        "max_retries": 3,
    },
    result_backend_transport_options={
        "visibility_timeout": 43200,
    },
    # ---------- Routing ----------
    task_default_queue="default",
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "high_priority": {"exchange": "high_priority", "routing_key": "high_priority"},
        "low_priority": {"exchange": "low_priority", "routing_key": "low_priority"},
    },
)
