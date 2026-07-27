"""Instância Celery — broker e result backend = Valkey (H12)."""

from celery import Celery

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

app = Celery(
    "market_dashboard",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
