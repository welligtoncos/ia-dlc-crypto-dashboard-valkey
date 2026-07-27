# Design da Aplicação — Consolidado

## Visão
Dashboard de cripto com padrão **BFF**: Angular apresenta; FastAPI orquestra via `MarketIndicatorsService`; Valkey cacheia; CoinGecko é a fonte; AWS via Terraform (tiers baratos).

## Decisões de design
- Orquestração no **MarketIndicatorsService** (rotas finas)
- API: `GET /api/indicators` com flag `degraded`
- UI: um `DashboardComponent` + `MarketApiService`; aviso global + por linha
- Infra no inception: componentes lógicos Network / CacheManaged / BffRuntime / FrontendCdn
- Arquivo extra aprovado: `backend/services/market_indicators.py`

## Artefatos
| Arquivo | Conteúdo |
|---|---|
| `components.md` | Componentes e responsabilidades |
| `component-methods.md` | Assinaturas de alto nível |
| `services.md` | Orquestração e princípios |
| `component-dependency.md` | Matriz e fluxos |

## Mapa para unidades (prévia)
| Unidade | Componentes principais |
|---|---|
| U1 BFF | AppConfig, MarketDataSource, CacheStore, IndicatorsEngine, MarketIndicatorsService, ApiRoutes, LocalStackRuntime |
| U2 Frontend | MarketApiService, DashboardComponent |
| U3 Infra | Network, CacheManaged, BffRuntime, FrontendCdn |

## Fora deste estágio
- Fórmulas detalhadas e propriedades PBT → Design Funcional U1
- Recursos Terraform concretos → Design de Infra U3 / Code Gen U3
