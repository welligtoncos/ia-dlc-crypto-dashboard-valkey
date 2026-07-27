# Esclarecimento — Design da Aplicação

Detectei contradição nas respostas:

- **Pergunta 1 = B**: inclui `MarketIndicatorsService` que **orquestra** e é chamado pelas rotas
- **Pergunta 3 = A**: orquestração fica nas **rotas** (`main.py`)

Essas opções não podem valer ao mesmo tempo para o mesmo fluxo.

---

## Pergunta de Esclarecimento 1
Onde deve ficar a orquestração cache → CoinGecko → indicadores?

A) Nas rotas (`main.py`) — manter P3=A; no design, **não** haverá Application Service dedicado (ajustar P1 para o modelo de 4 componentes: MarketDataSource/CoinGeckoClient, CacheStore, IndicatorsEngine, ApiRoutes)

B) No `MarketIndicatorsService` — manter P1=B; rotas só HTTP (ajustar P3 para B)

C) Híbrido explícito: rotas fazem só binding HTTP + tratamento de status; `MarketIndicatorsService` concentra cache/CoinGecko/indicadores (equivale a B, com rotas “finas”)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: B
