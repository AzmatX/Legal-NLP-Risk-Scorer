import os
from celery import Celery

# Read from environment (set in docker-compose.yml)
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "contract_intelligence",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,
)

# Automatically discover tasks from all registered modules
celery_app.autodiscover_tasks(["src.tasks"])

# Health check for broker
@celery_app.task(name="tasks.ping")
def ping():
    return "pong"