"""Configuração via variáveis de ambiente (sem segredos hardcoded)."""

import os


def _csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [p.strip() for p in raw.split(",") if p.strip()]


# CORS (H19) — origens permitidas (localhost + CloudFront em prod via env).
CORS_ORIGINS: list[str] = _csv_env(
    "CORS_ORIGINS",
    "http://localhost:4200,http://127.0.0.1:4200",
)

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

# Celery (H12) — broker e result backend = Valkey (mesmo host/porta por padrão).
_DEFAULT_CELERY_URL = f"redis://{VALKEY_HOST}:{VALKEY_PORT}/{VALKEY_DB}"
CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", _DEFAULT_CELERY_URL)
CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", _DEFAULT_CELERY_URL)

# Celery Beat (H13) — intervalo do batch proativo.
# Default 60s: alinhado ao TTL do cache; 3 moedas ≈ 3 req/min (API keyless ~10–50 req/min).
# Não reduzir agressivamente nem subir múltiplos beats (um único serviço beat no Compose).
BEAT_INTERVAL_SECONDS: int = int(os.getenv("BEAT_INTERVAL_SECONDS", "60"))

# Cache-aside (H06) — TTL do payload de indicadores em segundos.
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))


# Série temporal (H08) — máximo de pontos por moeda.
SERIES_MAX_POINTS: int = int(os.getenv("SERIES_MAX_POINTS", "100"))

# Indicadores (H09) — quantos preços recentes usar na média móvel.
SMA_WINDOW: int = int(os.getenv("SMA_WINDOW", "20"))
