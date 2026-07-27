"""Instância Celery — broker/backend Valkey (H12); Beat schedule (H13)."""

from celery import Celery

from config import (
    BEAT_INTERVAL_SECONDS,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
)

app = Celery(
    "market_dashboard",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

# Um único job periodico: 1 chamada CoinGecko em lote + pipeline por moeda.
# Evita 3 tasks simultaneas (causa frequente de HTTP 429).
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    beat_schedule={
        "processar-dashboard-lote": {
            "task": "tasks.processar_dashboard_batch",
            "schedule": float(BEAT_INTERVAL_SECONDS),
            "args": ("beat",),
        },
    },
)

# Carrega tasks + sinais para o log didatico.
import tasks as _tasks  # noqa: E402, F401
