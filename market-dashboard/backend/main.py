"""
BFF — Dashboard de Mercado (H02: mock).

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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    """Retorna indicadores mockados (sem CoinGecko / Valkey / Celery)."""
    return {
        "moeda": "bitcoin",
        "preco": 100000.0,
        "variacao_24h": 2.5,
        "media_movel": None,
        "volatilidade": None,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
