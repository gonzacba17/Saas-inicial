"""
Celery application for handling async tasks like notifications, analysis, and reports.
This service enables background processing for time-consuming operations.
"""
import os
from celery import Celery
from app.core.config import settings

# Redis URL configuration
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "saas_inicial",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.services.celery_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Time zone
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.services.celery_tasks.generate_ai_insights": {"queue": "ai_queue"},
        "app.services.celery_tasks.send_notification": {"queue": "notifications"},
        "app.services.celery_tasks.generate_business_report": {"queue": "reports"},
        "app.services.celery_tasks.process_payment_webhook": {"queue": "payments"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True,
    },
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    worker_prefetch_multiplier=1,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Retry policy
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Queue configuration
    task_default_queue="default",
    task_create_missing_queues=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "daily-business-report": {
            "task": "app.services.celery_tasks.generate_daily_business_reports",
            "schedule": 86400.0,  # Daily at midnight UTC
        },
        "cleanup-old-conversations": {
            "task": "app.services.celery_tasks.cleanup_old_ai_conversations",
            "schedule": 3600.0,  # Hourly
        },
        "update-analytics-cache": {
            "task": "app.services.celery_tasks.update_analytics_cache",
            "schedule": 1800.0,  # Every 30 minutes
        },
    },
)

# Health check function
def celery_health_check():
    """Check if Celery workers are responding."""
    try:
        # Send a test task
        result = celery_app.send_task("app.services.celery_tasks.health_check")
        # Wait for result with timeout
        return result.get(timeout=5) == "healthy"
    except Exception:
        return False

if __name__ == "__main__":
    # For running celery worker: python -m app.services.celery_app worker
    celery_app.start()