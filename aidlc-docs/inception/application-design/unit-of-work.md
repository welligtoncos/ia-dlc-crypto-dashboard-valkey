# Unidades de Trabalho — market-dashboard

## Organização de código (greenfield)

```text
market-dashboard/
  backend/                 # U1
  frontend/                # U2 (placeholder possível na U1 via Compose)
  infra/                   # U3
  docker-compose.yml       # U1 (Valkey + backend + frontend)
```

Raiz do workspace AI-DLC: `c:\welligton-aws\ia-dlc-crypto-dashboard-valkey`  
Código da aplicação: sob `market-dashboard/` (nunca em `aidlc-docs/`).

---

## U1 — BFF + Valkey local + indicadores

| Atributo | Valor |
|---|---|
| **Tipo** | Serviço (container FastAPI) + runtime local Compose |
| **Responsabilidade** | Config, CoinGecko, cache Valkey, indicadores, `MarketIndicatorsService`, API `GET /api/indicators`, Compose completo |
| **Componentes** | AppConfig, MarketDataSource, CacheStore, IndicatorsEngine, MarketIndicatorsService, ApiRoutes, LocalStackRuntime |
| **Pasta** | `market-dashboard/backend/` + `docker-compose.yml` |
| **Deploy** | Container BFF; local via Compose (Valkey+backend+frontend; FE pode ser placeholder até U2) |
| **Checklist interno** | US-BFF-01 → US-BFF-06 |
| **Estágios Construction** | Design Funcional EXECUTE; NFR EXECUTE (PBT/TTL); Infra Design SKIP; Code Gen EXECUTE |

### Critério de pronto da unidade
- Endpoint de indicadores para BTC/ETH/SOL com cache e degradação
- Compose sobe a stack local
- Sem lógica de indicadores no cache wrapper

---

## U2 — Frontend Angular

| Atributo | Valor |
|---|---|
| **Tipo** | Módulo/artefato estático (SPA) |
| **Responsabilidade** | App Angular standalone, environment, HttpClient, tabela + atualizar + avisos de degradação |
| **Componentes** | MarketApiService, DashboardComponent |
| **Pasta** | `market-dashboard/frontend/` |
| **Deploy** | Build estático; Compose atualizado se o FE da U1 era placeholder |
| **Checklist interno** | US-FE-01 → US-FE-03 |
| **Estágios Construction** | Design Funcional SKIP/mínimo; NFR mínimo; Infra Design SKIP; Code Gen EXECUTE |

### Critério de pronto da unidade
- Painel consome só o BFF; sem cálculos no cliente
- URL da API via environment

---

## U3 — Infra Terraform AWS

| Atributo | Valor |
|---|---|
| **Tipo** | IaC (não é serviço de domínio) |
| **Responsabilidade** | Provisionar Network, ElastiCache Valkey, ECR/ECS/ALB, S3/CloudFront em `us-east-1` (tiers baratos) |
| **Componentes** | Network, CacheManaged, BffRuntime, FrontendCdn |
| **Pasta** | `market-dashboard/infra/` |
| **Deploy** | Publica U1 (BFF) e U2 (estático) na AWS |
| **Checklist interno** | US-INF-01 → US-INF-04 |
| **Estágios Construction** | Design Funcional SKIP; NFR EXECUTE (custo/sizing); Infra Design EXECUTE; Code Gen EXECUTE |

### Critério de pronto da unidade
- `terraform plan` revisado antes de `apply`
- Outputs: DNS ALB, URL CDN
- Lembrete de `terraform destroy` ao fim do estudo

---

## Sequência de construção
1. Completar **U1**  
2. Completar **U2**  
3. Completar **U3**  
4. Build e Testes consolidados  

**Paralelismo**: nenhum (sequência estrita).
