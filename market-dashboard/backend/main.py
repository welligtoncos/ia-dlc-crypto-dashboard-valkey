"""
BFF — Dashboard de Mercado (H04: dado real via CoinGecko, sem cache).

Contrato GET /api/dashboard (JSON):
- moeda: str
- preco: float
- variacao_24h: float
- media_movel: float | null
- volatilidade: float | null
- atualizado_em: str (ISO-8601)

Espelhado no frontend em src/app/models/moeda-card.model.ts (DashboardItem).
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import DASHBOARD_COIN_ID
from services.coingecko import CoinGeckoError, get_market_data

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
