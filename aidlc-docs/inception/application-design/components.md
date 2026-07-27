# Componentes — market-dashboard (revisão)

## Backend
| Componente | Arquivo | Responsabilidade |
|---|---|---|
| ApiRoutes | `main.py` | `GET /api/dashboard`, CORS, header X-Cache, orquestra HIT/MISS chamando pipeline |
| AppConfig | `config.py` | TTL, moedas, URLs, Valkey/broker, N da série, intervalo beat |
| CoinGeckoClient | `services/coingecko.py` | `get_market_data` — só fonte externa |
| CacheStore | `services/cache.py` | get/set/ping/série — sem negócio |
| IndicatorsEngine | `services/indicators.py` | `media_movel`, `volatilidade` — puro |
| Pipeline | `services/pipeline.py` | Único caminho coleta→série→cálculo→cache (rota MISS e Celery) |
| CeleryApp | `celery_app.py` | Broker/backend = Valkey |
| CeleryTasks | `tasks.py` | Task que chama `pipeline.processar_moeda` |
| BeatSchedule | config Celery Beat | Agenda periódica (1 beat) |

## Frontend
| Componente | Responsabilidade |
|---|---|
| CardMoeda | Exibe campos via `@Input`; "—" para null |
| Dashboard (pai) | Lista cards; estado de erro |
| DashboardService | HttpClient → `/api/dashboard`; URL via environment |

## Infra lógica
Network · EcrRepo · CacheManaged · EcsBff · EcsWorker · EcsBeat · Alb · FrontendCdn · CiCd (H20)

## Local
Compose: `valkey` + `backend` + `worker` + `beat` (FE via `ng serve` nas fases locais)
