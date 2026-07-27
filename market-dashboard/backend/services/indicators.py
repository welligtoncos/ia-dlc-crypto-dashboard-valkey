"""
Cálculos de indicadores (puros).

Sem I/O de rede/cache — a rota (ou pipeline futuro) só orquestra.
"""

from __future__ import annotations


def media_movel(precos: list[float]) -> float | None:
    """
    Média aritmética simples dos preços informados.

    Retorna None se não houver pontos suficientes (< 2).
    Ex.: media_movel([100, 102, 101, 103, 104]) == 102.0
    """
    if len(precos) < 2:
        return None
    return sum(precos) / len(precos)
