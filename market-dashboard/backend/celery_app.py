"""Instância Celery — broker/backend Valkey (H12); Beat schedule (H13)."""

from celery import Celery

from config import (
    BEAT_INTERVAL_SECONDS,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    DASHBOARD_COIN_IDS,
)

app = Celery(
    "market_dashboard",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

# Uma entrada de schedule por moeda; um único processo beat no Compose (sem agendadores duplicados).
_beat_schedule = {
    f"processar-moeda-{coin_id}": {
        "task": "tasks.processar_moeda_task",
        "schedule": float(BEAT_INTERVAL_SECONDS),
        "args": (coin_id,),
    }
    for coin_id in DASHBOARD_COIN_IDS
}

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule=_beat_schedule,
)
