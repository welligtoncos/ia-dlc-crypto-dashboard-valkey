# Dependências — revisão

```text
CardMoeda <- Dashboard <- DashboardService --HTTP--> ApiRoutes
                                                      |
                                      HIT: CacheStore |
                                      MISS: Pipeline ------+
                                              |            |
                                    CoinGeckoClient   IndicatorsEngine
                                              |            |
                                              +--> CacheStore (resultado + série)

Celery Beat --> CeleryTasks --> Pipeline --> (mesmas deps)
Worker conecta Valkey (broker + dados)
```

## Matriz
| De | Para |
|---|---|
| ApiRoutes | CacheStore, Pipeline, AppConfig |
| Pipeline | CoinGeckoClient, CacheStore, IndicatorsEngine, AppConfig |
| CeleryTasks | Pipeline |
| Beat | CeleryTasks (via broker) |
| DashboardService | ApiRoutes (HTTP) |
| EcsBff/Worker/Beat | CacheManaged, EcrRepo, Network |
| FrontendCdn | build Angular |
