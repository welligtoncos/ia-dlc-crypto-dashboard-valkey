"""Tarefas Celery — delegam ao pipeline (H12). Sem beat ainda (H13)."""

from __future__ import annotations

from typing import Any

from celery_app import app
from services.pipeline import processar_moeda


@app.task(name="tasks.processar_moeda_task")
def processar_moeda_task(coin_id: str) -> dict[str, Any]:
    """Executa o mesmo pipeline da rota MISS, de forma assíncrona."""
    return processar_moeda(coin_id)
