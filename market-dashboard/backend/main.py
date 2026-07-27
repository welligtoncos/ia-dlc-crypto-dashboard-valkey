"""
BFF — Dashboard de Mercado.

Contrato GET /api/dashboard (H11+): lista JSON de objetos
- moeda: str
- preco: float
- variacao_24h: float
- media_movel: float | null
- volatilidade: float | null
- atualizado_em: str (ISO-8601)

Espelhado no frontend em src/app/models/moeda-card.model.ts (DashboardItem).

H05–H11: health, cache-aside, X-Cache, série, SMA, volatilidade, multi-moeda.
H12: MISS via pipeline.py (mesmo caminho da task Celery).
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, DASHBOARD_COIN_IDS, SERIES_MAX_POINTS, SMA_WINDOW
from services.cache import get as cache_get
from services.cache import get_ultimos_pontos
from services.cache import ping as valkey_ping
from services.cache import serie_key
from services.coingecko import CoinGeckoError
from services.indicators import media_movel
from services.observability import emit, list_events
from services.pipeline import cache_key, processar_moedas

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="market-dashboard-bff", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Cache"],
)


@app.on_event("startup")
def log_valkey_connection() -> None:
    ok = valkey_ping()
    if ok:
        logger.info("Valkey PING ok — BFF conectado ao cache")
    else:
        logger.warning("Valkey PING falhou no startup (BFF sobe mesmo assim)")
    logger.info("moedas configuradas: %s", DASHBOARD_COIN_IDS)
    logger.info("CORS_ORIGINS: %s", CORS_ORIGINS)


@app.get("/health")
def health() -> dict:
    """Healthcheck: confirma se o BFF fala com o Valkey (PING)."""
    ok = valkey_ping()
    status = "ok" if ok else "degraded"
    return {"status": status, "valkey": ok, "moedas": DASHBOARD_COIN_IDS}


@app.get("/api/dashboard")
def get_dashboard(
    response: Response,
    refresh: bool = Query(False, description="Se true, ignora cache e força MISS"),
) -> list[dict[str, Any]]:
    """
    H11: uma entrada por moeda em DASHBOARD_COIN_IDS.
    HIT por moeda no Valkey; MISS em lote (1 request CoinGecko) para reduzir 429.
    """
    started = time.perf_counter()
    if not DASHBOARD_COIN_IDS:
        raise HTTPException(status_code=500, detail="Nenhuma moeda configurada em DASHBOARD_COIN_IDS")

    por_moeda: dict[str, dict[str, Any]] = {}
    origens: dict[str, str] = {}
    misses: list[str] = []

    for coin_id in DASHBOARD_COIN_IDS:
        key = cache_key(coin_id)
        if not refresh:
            cached = cache_get(key)
            if isinstance(cached, dict):
                por_moeda[coin_id] = cached
                origens[coin_id] = "HIT"
                continue
        emit(
            "valkey_cache",
            "Valkey STRING+TTL",
            f"MISS — chave ausente/expirada {key}",
            detail={"chave": key, "moeda": coin_id, "refresh": refresh},
        )
        emit(
            "bff",
            "FastAPI BFF",
            f"MISS {coin_id} — entrara no lote CoinGecko",
            detail={"moeda": coin_id, "origem": "MISS"},
        )
        misses.append(coin_id)

    if misses:
        try:
            for payload in processar_moedas(misses):
                cid = str(payload.get("moeda"))
                por_moeda[cid] = payload
                origens[cid] = "MISS"
        except CoinGeckoError as exc:
            logger.error("falha no lote CoinGecko misses=%s erro=%s", misses, exc)

    items = [por_moeda[c] for c in DASHBOARD_COIN_IDS if c in por_moeda]
    if not items:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter dados da CoinGecko para nenhuma moeda configurada.",
        )

    origem_list = [origens[c] for c in DASHBOARD_COIN_IDS if c in origens]
    origem_geral = "HIT" if origem_list and all(o == "HIT" for o in origem_list) else "MISS"
    response.headers["X-Cache"] = origem_geral
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "dashboard origem=%s coins_ok=%s/%s latencia_ms=%.2f refresh=%s",
        origem_geral,
        len(items),
        len(DASHBOARD_COIN_IDS),
        elapsed_ms,
        refresh,
    )
    emit(
        "bff",
        "FastAPI BFF",
        f"GET /api/dashboard X-Cache={origem_geral} "
        f"ok={len(items)}/{len(DASHBOARD_COIN_IDS)} {elapsed_ms:.0f}ms",
        detail={"origem": origem_geral, "latencia_ms": round(elapsed_ms, 2)},
    )
    return items


@app.get("/api/observability/events")
def get_observability_events(limit: int = Query(50, ge=1, le=100)) -> list[dict[str, Any]]:
    """Historico didatico recente (Valkey LIST) — BFF, pipeline, Beat, Worker, Valkey, CoinGecko."""
    return list_events(limit=limit)


@app.get("/api/series/{moeda}")
def get_serie(
    moeda: str,
    limit: int = Query(40, ge=2, le=100, description="Quantos pontos retornar (mais recentes)"),
) -> dict[str, Any]:
    """
    Histórico de preços da série Valkey (ZSET) para acompanhar a MM.

    Para cada ponto, media_movel é a média da janela SMA_WINDOW terminando naquele ponto
    (None se ainda não houver pontos suficientes). Cálculo no BFF — Angular só exibe.
    """
    coin_id = moeda.strip().lower()
    if coin_id not in DASHBOARD_COIN_IDS:
        raise HTTPException(
            status_code=404,
            detail=f"Moeda '{coin_id}' não está em DASHBOARD_COIN_IDS.",
        )

    n = min(limit, SERIES_MAX_POINTS)
    brutos = get_ultimos_pontos(coin_id, n)
    precos = [float(p["preco"]) for p in brutos]
    pontos: list[dict[str, Any]] = []
    for i, p in enumerate(brutos):
        # MM completa só com janela SMA_WINDOW (igual ao pipeline).
        if i + 1 >= SMA_WINDOW:
            janela = precos[i + 1 - SMA_WINDOW : i + 1]
            mm = media_movel(janela)
        else:
            mm = None
        pontos.append(
            {
                "ts": p["ts"],
                "preco": p["preco"],
                "media_movel": mm,
            }
        )

    return {
        "moeda": coin_id,
        "chave": serie_key(coin_id),
        "janela_sma": SMA_WINDOW,
        "total": len(pontos),
        "pontos": pontos,
    }
