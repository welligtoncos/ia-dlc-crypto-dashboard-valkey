"""Configuração via variáveis de ambiente (sem segredos hardcoded)."""

import os


# API pública keyless: ~10–50 req/min — evite polling agressivo (cache vem nas próximas histórias).
COINGECKO_BASE_URL: str = os.getenv(
    "COINGECKO_BASE_URL",
    "https://api.coingecko.com/api/v3",
)
COINGECKO_TIMEOUT_SECONDS: float = float(os.getenv("COINGECKO_TIMEOUT_SECONDS", "10"))
COINGECKO_VS_CURRENCY: str = os.getenv("COINGECKO_VS_CURRENCY", "usd")
