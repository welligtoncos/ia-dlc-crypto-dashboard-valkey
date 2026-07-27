"""
Wrapper fino do Valkey via redis-py.

Responsabilidades:
- get/set/ping com JSON (cache de resultado)
- série temporal de preços (H08) — sem cálculo de indicadores

Escolha da série (H08): Sorted Set (ZSET).
- score = timestamp Unix (float/ms)
- member = "{timestamp}:{preco}" (único mesmo com preço repetido)
- trim com ZREMRANGEBYRANK para manter só os últimos N
Motivo: ordenação cronológica nativa e limite de tamanho simples.
"""

from __future__ import annotations

import json
import logging
import time
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


def serie_key(coin_id: str) -> str:
    return f"serie:{coin_id}:precos"


def append_preco(
    coin_id: str,
    preco: float,
    *,
    max_n: int,
    timestamp: float | None = None,
) -> None:
    """
    Adiciona um ponto (preço + timestamp) na série ZSET e mantém no máximo max_n pontos.
    """
    if max_n < 1:
        raise ValueError("max_n deve ser >= 1")

    ts = time.time() if timestamp is None else timestamp
    key = serie_key(coin_id)
    member = f"{ts}:{preco}"
    client = _get_client()
    client.zadd(key, {member: ts})
    # Remove os mais antigos se passar de N (índices 0 .. -(max_n+1))
    excess = client.zcard(key) - max_n
    if excess > 0:
        client.zremrangebyrank(key, 0, excess - 1)


def get_ultimos_precos(coin_id: str, n: int) -> list[float]:
    """
    Retorna os últimos n preços em ordem cronológica (mais antigo → mais recente).
    """
    if n < 1:
        return []

    key = serie_key(coin_id)
    # ZRANGE com start negativo: últimos n members ordenados por score asc
    members = _get_client().zrange(key, -n, -1)
    precos: list[float] = []
    for member in members:
        # member = "{ts}:{preco}" — preço é o trecho após o primeiro ':'
        try:
            precos.append(float(member.split(":", 1)[1]))
        except (IndexError, ValueError):
            logger.warning("membro de série inválido: %s", member)
    return precos
