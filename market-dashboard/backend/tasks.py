"""Tarefas Celery — lote CoinGecko + pipeline; sinais para o log didatico."""

from __future__ import annotations

from typing import Any

from celery.signals import (
    after_task_publish,
    task_failure,
    task_postrun,
    task_prerun,
)

from celery_app import app
from config import DASHBOARD_COIN_IDS
from services.observability import emit
from services.pipeline import processar_moeda, processar_moedas


def _task_name(sender: Any, headers: Any) -> str | None:
    if isinstance(sender, str):
        return sender
    name = getattr(sender, "name", None)
    if name:
        return name
    return (headers or {}).get("task")


@after_task_publish.connect
def _on_after_publish(sender=None, headers=None, body=None, **kwargs: Any) -> None:
    name = _task_name(sender, headers)
    if name != "tasks.processar_dashboard_batch":
        return
    # Didatico: mostra as 3 moedas "entrando" na fila (1 task real no broker).
    for coin_id in DASHBOARD_COIN_IDS:
        emit(
            "beat",
            "Celery Beat → Valkey broker",
            f"Enfileirou processar_moeda_task({coin_id})",
            detail={"moeda": coin_id, "fila": "celery", "broker": "Valkey", "lote": True},
        )
        emit(
            "valkey_broker",
            "Valkey (broker Celery)",
            f"Mensagem na fila para {coin_id}",
            detail={"moeda": coin_id, "lote": True},
        )


@task_prerun.connect
def _on_task_prerun(sender=None, task_id=None, args=None, **kwargs: Any) -> None:
    name = getattr(sender, "name", None) if sender else None
    if name == "tasks.processar_dashboard_batch":
        emit(
            "beat",
            "Celery Beat (job agendado)",
            "Job periodico (lote) chegou ao worker",
            detail={"task_id": task_id, "moedas": DASHBOARD_COIN_IDS},
        )
        emit(
            "worker",
            "Celery Worker",
            "Task recebida da fila — processar lote dashboard",
            detail={"task_id": task_id, "origem": "beat", "lote": True},
        )
        for coin_id in DASHBOARD_COIN_IDS:
            emit(
                "valkey_broker",
                "Valkey (broker Celery)",
                f"Worker consumiu mensagem de {coin_id}",
                detail={"moeda": coin_id, "lote": True},
            )
        return

    if name != "tasks.processar_moeda_task":
        return
    coin_id = args[0] if args else None
    origem = args[1] if args and len(args) > 1 else "worker"
    if origem == "beat":
        emit(
            "beat",
            "Celery Beat (job agendado)",
            f"Job periodico chegou ao worker — {coin_id}",
            detail={"moeda": coin_id, "task_id": task_id},
        )
    emit(
        "worker",
        "Celery Worker",
        f"Task recebida da fila — processar {coin_id}",
        detail={"moeda": coin_id, "task_id": task_id, "origem": origem},
    )
    emit(
        "valkey_broker",
        "Valkey (broker Celery)",
        f"Worker consumiu mensagem de {coin_id}",
        detail={"moeda": coin_id},
    )


@task_postrun.connect
def _on_task_postrun(sender=None, task_id=None, args=None, state=None, **kwargs: Any) -> None:
    name = getattr(sender, "name", None) if sender else None
    if name == "tasks.processar_dashboard_batch":
        for coin_id in DASHBOARD_COIN_IDS:
            emit(
                "worker",
                "Celery Worker",
                f"Task concluida ({state}) — {coin_id}",
                detail={"moeda": coin_id, "task_id": task_id, "state": state, "lote": True},
            )
        return
    if name != "tasks.processar_moeda_task":
        return
    coin_id = args[0] if args else None
    emit(
        "worker",
        "Celery Worker",
        f"Task concluida ({state}) — {coin_id}",
        detail={"moeda": coin_id, "task_id": task_id, "state": state},
    )


@task_failure.connect
def _on_task_failure(sender=None, task_id=None, args=None, exception=None, **kwargs: Any) -> None:
    name = getattr(sender, "name", None) if sender else None
    if name == "tasks.processar_dashboard_batch":
        emit(
            "worker",
            "Celery Worker",
            f"Task FALHOU — lote dashboard: {exception}",
            detail={"task_id": task_id, "lote": True},
        )
        return
    if name != "tasks.processar_moeda_task":
        return
    coin_id = args[0] if args else None
    emit(
        "worker",
        "Celery Worker",
        f"Task FALHOU — {coin_id}: {exception}",
        detail={"moeda": coin_id, "task_id": task_id},
    )


@app.task(name="tasks.processar_dashboard_batch")
def processar_dashboard_batch(origem: str = "beat") -> list[dict[str, Any]]:
    """
    Ciclo proativo: 1x CoinGecko (ids em lote) + pipeline por moeda.
    origem=beat quando agendado pelo Celery Beat.
    """
    return processar_moedas(DASHBOARD_COIN_IDS)


@app.task(name="tasks.processar_moeda_task")
def processar_moeda_task(coin_id: str, origem: str = "manual") -> dict[str, Any]:
    """Task unitaria (manual/debug). O Beat usa o lote."""
    return processar_moeda(coin_id)
