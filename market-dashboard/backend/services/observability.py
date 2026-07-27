"""
Log didatico: historico curto no Valkey (LIST) para o painel Angular.

Nao e CloudWatch — e um feed da aplicacao (BFF, pipeline, Beat, Worker, Valkey, CoinGecko).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from config import OBSERVABILITY_MAX_EVENTS
from services.cache import _get_client

logger = logging.getLogger(__name__)

EVENTS_KEY = "observability:events"


def emit(source: str, tech: str, message: str, *, detail: dict[str, Any] | None = None) -> None:
    """
    Grava um evento no inicio da LIST (LPUSH) e limita o tamanho (LTRIM).

    source: bff | pipeline | beat | worker | valkey_cache | valkey_serie | valkey_broker | coingecko
    tech: rotulo curto para o UI (ex: FastAPI, Celery Beat, Valkey ZSET)
    """
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "tech": tech,
        "message": message,
        "detail": detail or {},
    }
    try:
        client = _get_client()
        client.lpush(EVENTS_KEY, json.dumps(event, ensure_ascii=False))
        client.ltrim(EVENTS_KEY, 0, max(OBSERVABILITY_MAX_EVENTS - 1, 0))
    except Exception as exc:  # noqa: BLE001 — log didatico nao pode derrubar o fluxo
        logger.debug("observability emit falhou: %s", exc)


def list_events(limit: int = 50) -> list[dict[str, Any]]:
    """Retorna eventos mais recentes primeiro."""
    n = max(1, min(limit, OBSERVABILITY_MAX_EVENTS))
    try:
        client = _get_client()
        raw = client.lrange(EVENTS_KEY, 0, n - 1)
    except Exception as exc:  # noqa: BLE001
        logger.warning("observability list falhou: %s", exc)
        return []

    out: list[dict[str, Any]] = []
    for item in raw:
        try:
            out.append(json.loads(item))
        except json.JSONDecodeError:
            continue
    return out
