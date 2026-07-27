"""
Cliente da API pública CoinGecko.

Endpoint:
  GET {base}/simple/price?ids=a,b,c&vs_currencies={vs}&include_24hr_change=true

Plano keyless: rate limit baixo. Preferir 1 chamada em lote + retry em 429.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from config import (
    COINGECKO_BASE_URL,
    COINGECKO_MIN_INTERVAL_SECONDS,
    COINGECKO_TIMEOUT_SECONDS,
    COINGECKO_VS_CURRENCY,
)
from services.cache import _get_client

logger = logging.getLogger(__name__)

_RATE_KEY = "coingecko:last_request_ts"


class CoinGeckoError(Exception):
    """Erro tratado da integração CoinGecko (rede, HTTP ou formato)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _aguardar_rate_limit() -> None:
    """Espaça chamadas entre processos (BFF/worker) via Valkey."""
    try:
        client = _get_client()
        agora = time.time()
        raw = client.get(_RATE_KEY)
        if raw is not None:
            ultimo = float(raw)
            espera = COINGECKO_MIN_INTERVAL_SECONDS - (agora - ultimo)
            if espera > 0:
                logger.info("CoinGecko rate-gate: aguardando %.1fs", espera)
                time.sleep(espera)
        client.set(_RATE_KEY, str(time.time()))
    except Exception as exc:  # noqa: BLE001 — gate nao pode derrubar coleta
        logger.debug("CoinGecko rate-gate indisponivel: %s", exc)


def get_market_data_many(coin_ids: list[str]) -> dict[str, dict[str, float]]:
    """
    Busca preço e variação 24h para varias moedas em UMA request.

    Retorna: { coin_id: {"preco": float, "variacao_24h": float}, ... }
    """
    ids = [c.strip() for c in coin_ids if c and c.strip()]
    if not ids:
        raise CoinGeckoError("coin_ids é obrigatório")

    url = f"{COINGECKO_BASE_URL.rstrip('/')}/simple/price"
    params = {
        "ids": ",".join(ids),
        "vs_currencies": COINGECKO_VS_CURRENCY,
        "include_24hr_change": "true",
    }

    last_error: CoinGeckoError | None = None
    for tentativa in range(3):
        _aguardar_rate_limit()
        try:
            with httpx.Client(timeout=COINGECKO_TIMEOUT_SECONDS) as client:
                response = client.get(url, params=params)
        except httpx.TimeoutException as exc:
            last_error = CoinGeckoError("CoinGecko demorou demais para responder (timeout)")
            logger.error("CoinGecko timeout: %s", exc)
            time.sleep(2 * (tentativa + 1))
            continue
        except httpx.RequestError as exc:
            last_error = CoinGeckoError("Falha de rede ao consultar a CoinGecko")
            logger.error("CoinGecko rede: %s", exc)
            time.sleep(2 * (tentativa + 1))
            continue

        if response.status_code == 429:
            espera = 5 * (tentativa + 1)
            logger.warning("CoinGecko 429 — retry em %ss (tentativa %s)", espera, tentativa + 1)
            last_error = CoinGeckoError(
                "CoinGecko retornou status 429",
                status_code=429,
            )
            time.sleep(espera)
            continue

        if response.status_code != 200:
            raise CoinGeckoError(
                f"CoinGecko retornou status {response.status_code}",
                status_code=response.status_code,
            )

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise CoinGeckoError("Resposta da CoinGecko não é JSON válido") from exc

        vs = COINGECKO_VS_CURRENCY
        change_key = f"{vs}_24h_change"
        out: dict[str, dict[str, float]] = {}
        for coin_id in ids:
            coin_data = payload.get(coin_id)
            if not isinstance(coin_data, dict):
                logger.warning("CoinGecko sem dados para %s", coin_id)
                continue
            price = coin_data.get(vs)
            change = coin_data.get(change_key)
            if price is None or change is None:
                logger.warning("CoinGecko formato inesperado %s=%s", coin_id, coin_data)
                continue
            try:
                out[coin_id] = {
                    "preco": float(price),
                    "variacao_24h": float(change),
                }
            except (TypeError, ValueError):
                logger.warning("CoinGecko valores inválidos %s=%s", coin_id, coin_data)
        if not out:
            raise CoinGeckoError("CoinGecko não retornou dados para nenhuma moeda pedida")
        return out

    assert last_error is not None
    raise last_error


def get_market_data(coin_id: str) -> dict[str, float]:
    """
    Busca preço atual e variação % 24h para um coin_id.
    Internamente usa o endpoint em lote (1 id).
    """
    if not coin_id or not coin_id.strip():
        raise CoinGeckoError("coin_id é obrigatório")
    cid = coin_id.strip()
    many = get_market_data_many([cid])
    if cid not in many:
        raise CoinGeckoError(f"Moeda '{cid}' não encontrada na CoinGecko")
    return many[cid]
