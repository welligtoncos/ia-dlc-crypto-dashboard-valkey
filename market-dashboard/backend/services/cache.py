"""
Wrapper fino do Valkey via redis-py.

Responsabilidade: get/set/ping com JSON. Sem lógica de negócio nem cálculo.
Uso na rota (cache-aside) começa na H06 — esta história só conecta e expõe o wrapper.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import redis

from config import VALKEY_DB, VALKEY_HOST, VALKEY_PORT

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis(
            host=VALKEY_HOST,
            port=VALKEY_PORT,
            db=VALKEY_DB,
            decode_responses=True,
        )
    return _client


def ping() -> bool:
    """Retorna True se o Valkey responder PING."""
    try:
        return bool(_get_client().ping())
    except redis.RedisError as exc:
        logger.error("Valkey PING falhou: %s", exc)
        return False


def get(chave: str) -> dict[str, Any] | list[Any] | None:
    """Lê JSON da chave; None se ausente."""
    raw = _get_client().get(chave)
    if raw is None:
        return None
    return json.loads(raw)


def set(chave: str, valor: dict[str, Any] | list[Any], ttl: int | None = None) -> None:
    """Grava JSON; ttl opcional em segundos."""
    payload = json.dumps(valor)
    client = _get_client()
    if ttl is not None:
        client.set(chave, payload, ex=ttl)
    else:
        client.set(chave, payload)
