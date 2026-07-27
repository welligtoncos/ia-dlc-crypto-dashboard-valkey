# Serviços e Orquestração

## Serviços de aplicação

### MarketIndicatorsService (orquestrador)
**Padrão**: Application Service no BFF.

Fluxo lógico de `get_indicators()`:
1. Para cada moeda configurada (BTC, ETH, SOL), tentar ler cache de payload/séries relevantes.
2. Em miss: chamar `MarketDataSource` (CoinGecko).
3. Calcular indicadores via `IndicatorsEngine`.
4. Persistir no `CacheStore` com TTLs de config.
5. Se fonte falhar e houver stale: retornar dados com `degraded=true` (global e/ou por moeda).
6. Se fonte falhar sem cache: erro de aplicação → rotas respondem 502/503.

### MarketApiService (frontend)
**Padrão**: Gateway HTTP fino.
- Única dependência de rede do Angular: BFF.
- Propaga erro HTTP para o `DashboardComponent`.

## Serviços de infraestrutura (lógicos)
| Serviço lógico | Papel |
|---|---|
| Network | Isolamento de rede |
| CacheManaged | Valkey gerenciado |
| BffRuntime | Execução do container BFF + entrada ALB |
| FrontendCdn | Distribuição estática |
| LocalStackRuntime | Compose local (Valkey+BFF+FE) |

## Princípios de orquestração
- Rotas HTTP **não** orquestram cache/fonte/cálculo.
- `CacheStore` e `IndicatorsEngine` **não** se chamam mutuamente.
- Frontend **nunca** chama CoinGecko.
