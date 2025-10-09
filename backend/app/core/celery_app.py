"""
Celery configuration for async task processing and scheduled jobs.
"""
import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

celery_app = Celery(
    "saas_cafeterias",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    include=[
        "app.tasks.notification_tasks",
        "app.tasks.scheduled_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Argentina/Buenos_Aires",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "check-vencimientos-diarios": {
        "task": "app.tasks.scheduled_tasks.check_vencimientos_proximos",
        "schedule": crontab(hour=9, minute=0),
    },
    "daily-summary": {
        "task": "app.tasks.scheduled_tasks.send_daily_summary",
        "schedule": crontab(hour=18, minute=0),
    },
    "weekly-report": {
        "task": "app.tasks.scheduled_tasks.send_weekly_report",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),
    },
}

if __name__ == "__main__":
    celery_app.start()
