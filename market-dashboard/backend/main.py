"""
BFF — Dashboard de Mercado.

Contrato GET /api/dashboard (JSON):
- moeda: str
- preco: float
- variacao_24h: float
- media_movel: float | null
- volatilidade: float | null
- atualizado_em: str (ISO-8601)

Espelhado no frontend em src/app/models/moeda-card.model.ts (DashboardItem).

H05: GET /health (PING Valkey).
H06: cache-aside com TTL configurável.
H07: header X-Cache, log de latência, ?refresh=true.
H08: no MISS, acumula preço na série Valkey (sem calcular indicadores).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

from config import CACHE_TTL_SECONDS, DASHBOARD_COIN_ID, SERIES_MAX_POINTS
from services.cache import append_preco
from services.cache import get as cache_get
from services.cache import ping as valkey_ping
from services.cache import set as cache_set
from services.coingecko import CoinGeckoError, get_market_data

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="market-dashboard-bff", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
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


@app.get("/health")
def health() -> dict:
    """Healthcheck: confirma se o BFF fala com o Valkey (PING)."""
    ok = valkey_ping()
    status = "ok" if ok else "degraded"
    return {"status": status, "valkey": ok}


def _cache_key(coin_id: str) -> str:
    return f"dashboard:{coin_id}:indicadores"


@app.get("/api/dashboard")
def get_dashboard(
    response: Response,
    refresh: bool = Query(False, description="Se true, ignora cache e força MISS"),
) -> dict[str, Any]:
    """
    Cache-aside + observabilidade (H07): X-Cache HIT|MISS e log com latência em ms.
    """
    started = time.perf_counter()
    coin_id = DASHBOARD_COIN_ID
    key = _cache_key(coin_id)
    origem = "MISS"

    if not refresh:
        cached = cache_get(key)
        if isinstance(cached, dict):
            origem = "HIT"
            response.headers["X-Cache"] = origem
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "dashboard origem=%s key=%s latencia_ms=%.2f refresh=%s",
                origem,
                key,
                elapsed_ms,
                refresh,
            )
            return cached

    logger.info("cache MISS key=%s refresh=%s — consultando CoinGecko", key, refresh)
    try:
        market = get_market_data(coin_id)
    except CoinGeckoError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.error(
            "dashboard origem=ERROR key=%s latencia_ms=%.2f erro=%s",
            key,
            elapsed_ms,
            exc,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "Não foi possível obter dados da fonte externa (CoinGecko). "
                f"{exc}"
            ),
        ) from exc

    preco = float(market["preco"])
    append_preco(coin_id, preco, max_n=SERIES_MAX_POINTS)
    logger.info(
        "serie atualizada coin=%s preco=%s max_n=%s",
        coin_id,
        preco,
        SERIES_MAX_POINTS,
    )

    payload: dict[str, Any] = {
        "moeda": coin_id,
        "preco": preco,
        "variacao_24h": market["variacao_24h"],
        "media_movel": None,
        "volatilidade": None,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    cache_set(key, payload, ttl=CACHE_TTL_SECONDS)
    response.headers["X-Cache"] = origem
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "dashboard origem=%s key=%s latencia_ms=%.2f refresh=%s",
        origem,
        key,
        elapsed_ms,
        refresh,
    )
    return payload
