"""
Celery Application Configuration

Configures Celery with Redis as broker and result backend.
Defines task routing, serialization, and retry policies.
"""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "dail_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Retry & limits
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=3,

    # Rate limiting for CourtListener API tasks
    task_default_rate_limit="10/m",

    # Task routing
    task_routes={
        "app.tasks.ingestion_tasks.*": {"queue": "ingestion"},
        "app.tasks.classification_tasks.*": {"queue": "classification"},
        "app.tasks.sync_tasks.*": {"queue": "sync"},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        "sync-courtlistener-hourly": {
            "task": "app.tasks.sync_tasks.poll_courtlistener_alerts",
            "schedule": 3600.0,  # 1 hour
        },
        "update-search-vectors-daily": {
            "task": "app.tasks.sync_tasks.refresh_search_vectors",
            "schedule": 86400.0,  # 24 hours
        },
    },
)

# Auto-discover tasks in the tasks package
celery_app.autodiscover_tasks(["app.tasks"])
