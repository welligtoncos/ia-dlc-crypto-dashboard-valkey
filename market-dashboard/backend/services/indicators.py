"""
Cálculos de indicadores (puros).

Sem I/O de rede/cache — a rota (ou pipeline futuro) só orquestra.
"""

from __future__ import annotations

import statistics


def media_movel(precos: list[float]) -> float | None:
    """
    Média aritmética simples dos preços informados.

    Retorna None se não houver pontos suficientes (< 2).
    Ex.: media_movel([100, 102, 101, 103, 104]) == 102.0
    """
    if len(precos) < 2:
        return None
    return sum(precos) / len(precos)


def volatilidade(precos: list[float]) -> float | None:
    """
    Volatilidade da janela de preços.

    Definição (documentada — H10):
    - Usa **retornos simples** r_i = (p_i - p_{i-1}) / p_{i-1}
    - Aplica **desvio-padrão amostral** (ddof=1) sobre os retornos
    - Resultado em **percentual** (× 100)

    Retorna None se houver menos de 3 preços (precisa de ≥ 2 retornos
    para o desvio amostral) ou se algum preço base for zero.
    """
    if len(precos) < 3:
        return None

    retornos: list[float] = []
    for anterior, atual in zip(precos, precos[1:]):
        if anterior == 0:
            return None
        retornos.append((atual - anterior) / anterior)

    if len(retornos) < 2:
        return None

    # statistics.stdev = desvio-padrão amostral (n-1)
    return statistics.stdev(retornos) * 100.0
