"""
Caminho único MISS: coleta → série → indicadores → cache.

Usado pela rota (MISS) e pela task Celery — sem duplicar lógica.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from config import CACHE_TTL_SECONDS, SERIES_MAX_POINTS, SMA_WINDOW
from services.cache import append_preco
from services.cache import get_ultimos_precos
from services.cache import set as cache_set
from services.coingecko import get_market_data
from services.indicators import media_movel, volatilidade

logger = logging.getLogger(__name__)


def cache_key(coin_id: str) -> str:
    return f"dashboard:{coin_id}:indicadores"


def processar_moeda(coin_id: str) -> dict[str, Any]:
    """
    Executa o pipeline completo para uma moeda e grava no Valkey.
    Levanta CoinGeckoError se a fonte falhar.
    """
    key = cache_key(coin_id)
    logger.info("pipeline processar_moeda coin=%s", coin_id)

    market = get_market_data(coin_id)
    preco = float(market["preco"])
    append_preco(coin_id, preco, max_n=SERIES_MAX_POINTS)

    precos = get_ultimos_precos(coin_id, SMA_WINDOW)
    payload: dict[str, Any] = {
        "moeda": coin_id,
        "preco": preco,
        "variacao_24h": market["variacao_24h"],
        "media_movel": media_movel(precos),
        "volatilidade": volatilidade(precos),
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    cache_set(key, payload, ttl=CACHE_TTL_SECONDS)
    return payload
