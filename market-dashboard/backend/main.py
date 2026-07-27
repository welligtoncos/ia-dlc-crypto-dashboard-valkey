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

from config import DASHBOARD_COIN_IDS
from services.cache import get as cache_get
from services.cache import ping as valkey_ping
from services.coingecko import CoinGeckoError
from services.pipeline import cache_key, processar_moeda

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
    logger.info("moedas configuradas: %s", DASHBOARD_COIN_IDS)


@app.get("/health")
def health() -> dict:
    """Healthcheck: confirma se o BFF fala com o Valkey (PING)."""
    ok = valkey_ping()
    status = "ok" if ok else "degraded"
    return {"status": status, "valkey": ok, "moedas": DASHBOARD_COIN_IDS}


def _build_coin_payload(coin_id: str, *, refresh: bool) -> tuple[dict[str, Any], str]:
    """
    Retorna (payload, origem HIT|MISS) para uma moeda.
    HIT: lê cache. MISS/refresh: chama pipeline.processar_moeda (único caminho).
    Levanta CoinGeckoError se a fonte falhar no MISS.
    """
    key = cache_key(coin_id)

    if not refresh:
        cached = cache_get(key)
        if isinstance(cached, dict):
            return cached, "HIT"

    logger.info("cache MISS key=%s refresh=%s — pipeline", key, refresh)
    payload = processar_moeda(coin_id)
    return payload, "MISS"


@app.get("/api/dashboard")
def get_dashboard(
    response: Response,
    refresh: bool = Query(False, description="Se true, ignora cache e força MISS"),
) -> list[dict[str, Any]]:
    """
    H11: uma entrada por moeda em DASHBOARD_COIN_IDS.
    Falha em uma moeda não impede as demais; 502 só se nenhuma tiver sucesso.
    """
    started = time.perf_counter()
    if not DASHBOARD_COIN_IDS:
        raise HTTPException(status_code=500, detail="Nenhuma moeda configurada em DASHBOARD_COIN_IDS")

    items: list[dict[str, Any]] = []
    origens: list[str] = []

    for coin_id in DASHBOARD_COIN_IDS:
        try:
            payload, origem = _build_coin_payload(coin_id, refresh=refresh)
            items.append(payload)
            origens.append(origem)
        except CoinGeckoError as exc:
            logger.error("falha parcial coin=%s erro=%s", coin_id, exc)
            continue

    if not items:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter dados da CoinGecko para nenhuma moeda configurada.",
        )

    origem_geral = "HIT" if origens and all(o == "HIT" for o in origens) else "MISS"
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
    return items
