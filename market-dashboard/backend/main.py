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
H06: cache-aside na rota com TTL configurável.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import CACHE_TTL_SECONDS, DASHBOARD_COIN_ID
from services.cache import get as cache_get
from services.cache import ping as valkey_ping
from services.cache import set as cache_set
from services.coingecko import CoinGeckoError, get_market_data

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
def get_dashboard() -> dict[str, Any]:
    """
    Cache-aside (H06): HIT no Valkey; MISS busca CoinGecko, grava com CACHE_TTL_SECONDS.
    media_movel e volatilidade ficam null até as histórias de indicadores.
    """
    coin_id = DASHBOARD_COIN_ID
    key = _cache_key(coin_id)

    cached = cache_get(key)
    if isinstance(cached, dict):
        logger.info("cache HIT key=%s", key)
        return cached

    logger.info("cache MISS key=%s — consultando CoinGecko", key)
    try:
        market = get_market_data(coin_id)
    except CoinGeckoError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Não foi possível obter dados da fonte externa (CoinGecko). "
                f"{exc}"
            ),
        ) from exc

    payload: dict[str, Any] = {
        "moeda": coin_id,
        "preco": market["preco"],
        "variacao_24h": market["variacao_24h"],
        "media_movel": None,
        "volatilidade": None,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    cache_set(key, payload, ttl=CACHE_TTL_SECONDS)
    return payload
