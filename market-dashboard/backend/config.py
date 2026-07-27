"""Configuração via variáveis de ambiente (sem segredos hardcoded)."""

import os


# API pública keyless: ~10–50 req/min — evite polling agressivo (cache vem nas próximas histórias).
COINGECKO_BASE_URL: str = os.getenv(
    "COINGECKO_BASE_URL",
    "https://api.coingecko.com/api/v3",
)
COINGECKO_TIMEOUT_SECONDS: float = float(os.getenv("COINGECKO_TIMEOUT_SECONDS", "10"))
COINGECKO_VS_CURRENCY: str = os.getenv("COINGECKO_VS_CURRENCY", "usd")

# Moeda exibida no dashboard (H04 — uma moeda; multi vem depois).
DASHBOARD_COIN_ID: str = os.getenv("DASHBOARD_COIN_ID", "bitcoin")

# Valkey (H05) — host/porta via env; no Compose o host é o nome do serviço.
VALKEY_HOST: str = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT: int = int(os.getenv("VALKEY_PORT", "6379"))
VALKEY_DB: int = int(os.getenv("VALKEY_DB", "0"))

# Cache-aside (H06) — TTL do payload de indicadores em segundos.
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
