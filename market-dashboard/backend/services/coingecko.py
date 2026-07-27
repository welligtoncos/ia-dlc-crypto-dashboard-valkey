"""
Cliente da API pública CoinGecko.

Endpoint usado (docs atuais):
  GET {base}/simple/price?ids={coin_id}&vs_currencies={vs}&include_24hr_change=true

Plano gratuito / keyless: rate limit baixo (ordem de dezenas de calls/min).
Não ligar à rota nesta história (H03) — isso é H04.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from config import (
    COINGECKO_BASE_URL,
    COINGECKO_TIMEOUT_SECONDS,
    COINGECKO_VS_CURRENCY,
)

logger = logging.getLogger(__name__)


class CoinGeckoError(Exception):
    """Erro tratado da integração CoinGecko (rede, HTTP ou formato)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_market_data(coin_id: str) -> dict[str, float]:
    """
    Busca preço atual e variação % 24h para um coin_id CoinGecko (ex.: \"bitcoin\").

    Retorna: {\"preco\": float, \"variacao_24h\": float}
    Levanta CoinGeckoError em falha de rede, status != 200 ou payload inesperado.
    """
    if not coin_id or not coin_id.strip():
        raise CoinGeckoError("coin_id é obrigatório")

    url = f"{COINGECKO_BASE_URL.rstrip('/')}/simple/price"
    params = {
        "ids": coin_id.strip(),
        "vs_currencies": COINGECKO_VS_CURRENCY,
        "include_24hr_change": "true",
    }

    try:
        with httpx.Client(timeout=COINGECKO_TIMEOUT_SECONDS) as client:
            response = client.get(url, params=params)
    except httpx.TimeoutException as exc:
        logger.error("CoinGecko timeout para coin_id=%s: %s", coin_id, exc)
        raise CoinGeckoError("CoinGecko demorou demais para responder (timeout)") from exc
    except httpx.RequestError as exc:
        logger.error("CoinGecko falha de rede para coin_id=%s: %s", coin_id, exc)
        raise CoinGeckoError("Falha de rede ao consultar a CoinGecko") from exc

    if response.status_code != 200:
        logger.error(
            "CoinGecko HTTP %s para coin_id=%s body=%s",
            response.status_code,
            coin_id,
            response.text[:300],
        )
        raise CoinGeckoError(
            f"CoinGecko retornou status {response.status_code}",
            status_code=response.status_code,
        )

    try:
        payload: dict[str, Any] = response.json()
    except ValueError as exc:
        logger.error("CoinGecko JSON inválido para coin_id=%s", coin_id)
        raise CoinGeckoError("Resposta da CoinGecko não é JSON válido") from exc

    coin_data = payload.get(coin_id)
    if not isinstance(coin_data, dict):
        logger.error("CoinGecko sem dados para coin_id=%s payload=%s", coin_id, payload)
        raise CoinGeckoError(f"Moeda '{coin_id}' não encontrada na CoinGecko")

    vs = COINGECKO_VS_CURRENCY
    price = coin_data.get(vs)
    change_key = f"{vs}_24h_change"
    change = coin_data.get(change_key)

    if price is None or change is None:
        logger.error(
            "CoinGecko formato inesperado coin_id=%s data=%s",
            coin_id,
            coin_data,
        )
        raise CoinGeckoError(
            f"Formato inesperado da CoinGecko (faltam '{vs}' ou '{change_key}')"
        )

    try:
        return {
            "preco": float(price),
            "variacao_24h": float(change),
        }
    except (TypeError, ValueError) as exc:
        logger.error("CoinGecko valores não numéricos coin_id=%s data=%s", coin_id, coin_data)
        raise CoinGeckoError("Valores de preço/variação inválidos na CoinGecko") from exc
