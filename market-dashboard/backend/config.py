"""Configuração via variáveis de ambiente (sem segredos hardcoded)."""

import os


# API pública keyless: ~10–50 req/min — evite polling agressivo (cache vem nas próximas histórias).
COINGECKO_BASE_URL: str = os.getenv(
    "COINGECKO_BASE_URL",
    "https://api.coingecko.com/api/v3",
)
COINGECKO_TIMEOUT_SECONDS: float = float(os.getenv("COINGECKO_TIMEOUT_SECONDS", "10"))
COINGECKO_VS_CURRENCY: str = os.getenv("COINGECKO_VS_CURRENCY", "usd")

# Moedas do dashboard (H11) — lista separada por vírgula; nova moeda só na config.
_DASHBOARD_COINS_RAW: str = os.getenv(
    "DASHBOARD_COIN_IDS",
    "bitcoin,ethereum,solana",
)
DASHBOARD_COIN_IDS: list[str] = [
    c.strip() for c in _DASHBOARD_COINS_RAW.split(",") if c.strip()
]

# Valkey (H05) — host/porta via env; no Compose o host é o nome do serviço.
VALKEY_HOST: str = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT: int = int(os.getenv("VALKEY_PORT", "6379"))
VALKEY_DB: int = int(os.getenv("VALKEY_DB", "0"))

# Cache-aside (H06) — TTL do payload de indicadores em segundos.
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))

# Série temporal (H08) — máximo de pontos por moeda.
SERIES_MAX_POINTS: int = int(os.getenv("SERIES_MAX_POINTS", "100"))

# Indicadores (H09) — quantos preços recentes usar na média móvel.
SMA_WINDOW: int = int(os.getenv("SMA_WINDOW", "20"))
