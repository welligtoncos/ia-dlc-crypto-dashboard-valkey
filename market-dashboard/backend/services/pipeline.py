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
from services.coingecko import get_market_data, get_market_data_many
from services.indicators import media_movel, volatilidade
from services.observability import emit

logger = logging.getLogger(__name__)


def cache_key(coin_id: str) -> str:
    return f"dashboard:{coin_id}:indicadores"


def processar_moeda(
    coin_id: str,
    *,
    market: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Executa o pipeline completo para uma moeda e grava no Valkey.

    market opcional: evita nova chamada CoinGecko (lote do Beat / dashboard).
    Levanta CoinGeckoError se a fonte falhar e market nao foi passado.
    """
    key = cache_key(coin_id)
    logger.info("pipeline processar_moeda coin=%s market_injetado=%s", coin_id, market is not None)
    emit(
        "pipeline",
        "pipeline.py",
        f"Iniciando pipeline para {coin_id}",
        detail={"moeda": coin_id},
    )

    if market is None:
        emit(
            "coingecko",
            "CoinGecko API",
            f"Consultando preco/variacao de {coin_id}",
            detail={"moeda": coin_id},
        )
        market = get_market_data(coin_id)
        emit(
            "coingecko",
            "CoinGecko API",
            f"Resposta OK {coin_id} preco={market['preco']}",
            detail={"moeda": coin_id, "preco": market["preco"]},
        )
    else:
        emit(
            "coingecko",
            "CoinGecko API",
            f"Usando cotacao em lote para {coin_id} preco={market['preco']}",
            detail={"moeda": coin_id, "preco": market["preco"], "lote": True},
        )

    preco = float(market["preco"])

    emit(
        "valkey_serie",
        "Valkey ZSET",
        f"Append preco na serie serie:{coin_id}:precos",
        detail={"moeda": coin_id, "max_n": SERIES_MAX_POINTS},
    )
    append_preco(coin_id, preco, max_n=SERIES_MAX_POINTS)

    precos = get_ultimos_precos(coin_id, SMA_WINDOW)
    emit(
        "valkey_serie",
        "Valkey ZSET",
        f"Lidos {len(precos)} pontos da serie (janela SMA={SMA_WINDOW})",
        detail={"moeda": coin_id, "n": len(precos)},
    )

    mm = media_movel(precos)
    vol = volatilidade(precos)
    emit(
        "pipeline",
        "indicators.py",
        f"Calculo MM={mm} vol={vol} (no BFF/worker, nao no Angular)",
        detail={"moeda": coin_id, "media_movel": mm, "volatilidade": vol},
    )

    payload: dict[str, Any] = {
        "moeda": coin_id,
        "preco": preco,
        "variacao_24h": float(market["variacao_24h"]),
        "media_movel": mm,
        "volatilidade": vol,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    cache_set(key, payload, ttl=CACHE_TTL_SECONDS)
    emit(
        "valkey_cache",
        "Valkey STRING+TTL",
        f"Gravou cache {key} TTL={CACHE_TTL_SECONDS}s",
        detail={"chave": key, "ttl": CACHE_TTL_SECONDS},
    )
    emit(
        "pipeline",
        "pipeline.py",
        f"Pipeline concluido para {coin_id}",
        detail={"moeda": coin_id},
    )
    return payload


def processar_moedas(coin_ids: list[str]) -> list[dict[str, Any]]:
    """
    Uma chamada CoinGecko para todas as moedas, depois pipeline local por moeda.
    Reduz drasticamente risco de HTTP 429 no Beat.
    """
    ids = [c.strip() for c in coin_ids if c and c.strip()]
    if not ids:
        return []

    emit(
        "coingecko",
        "CoinGecko API",
        f"Consulta em lote ids={','.join(ids)}",
        detail={"moedas": ids, "lote": True},
    )
    markets = get_market_data_many(ids)
    emit(
        "coingecko",
        "CoinGecko API",
        f"Lote OK — {len(markets)}/{len(ids)} moedas",
        detail={"ok": list(markets.keys())},
    )

    out: list[dict[str, Any]] = []
    for coin_id in ids:
        m = markets.get(coin_id)
        if m is None:
            logger.error("lote sem cotacao para %s — pulando", coin_id)
            continue
        out.append(processar_moeda(coin_id, market=m))
    return out
