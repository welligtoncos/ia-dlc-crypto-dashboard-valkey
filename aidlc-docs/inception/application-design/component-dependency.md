# Dependências e Comunicação

## Matriz de dependência (BFF + FE)

| Componente | Depende de |
|---|---|
| ApiRoutes | MarketIndicatorsService, AppConfig |
| MarketIndicatorsService | MarketDataSource, CacheStore, IndicatorsEngine, AppConfig |
| MarketDataSource | AppConfig (URL), CoinGecko (externo) |
| CacheStore | AppConfig (host/TTL), Valkey |
| IndicatorsEngine | AppConfig (janelas) — sem I/O |
| MarketApiService | environment (URL BFF), HttpClient |
| DashboardComponent | MarketApiService |
| BffRuntime | Network, CacheManaged, imagem ECR |
| FrontendCdn | Network (edge), build Angular |
| CacheManaged | Network |

## Regras de acoplamento
- `CacheStore` ⟂ `IndicatorsEngine` (sem dependência mútua)
- Frontend → apenas contrato HTTP do BFF
- Infra lógica não contém regra de indicadores

## Fluxo de dados (texto)

```text
Visitante
   |
   v
DashboardComponent --> MarketApiService --HTTP--> ApiRoutes
                                                      |
                                                      v
                                         MarketIndicatorsService
                                          /         |          \
                                         v          v           v
                                   CacheStore  MarketData   IndicatorsEngine
                                         |      Source
                                         v          v
                                      Valkey    CoinGecko
```

## Fluxo de degradação

```text
CoinGecko falha
      |
      +--> cache stale? --sim--> resposta 200 + degraded=true
      |
      +--> sem cache ------> ApiRoutes responde 502/503
```
