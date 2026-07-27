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

H05: healthcheck Valkey em GET /health — cache-aside na rota só na H06.
"""

from datetime import datetime, timezone
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import DASHBOARD_COIN_ID
from services.cache import ping as valkey_ping
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


@app.get("/api/dashboard")
def get_dashboard() -> dict:
    """
    Busca preço/variação na CoinGecko a cada request (sem cache — intencional na H04).
    media_movel e volatilidade ficam null até as histórias de indicadores.
    """
    coin_id = DASHBOARD_COIN_ID
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

    return {
        "moeda": coin_id,
        "preco": market["preco"],
        "variacao_24h": market["variacao_24h"],
        "media_movel": None,
        "volatilidade": None,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
