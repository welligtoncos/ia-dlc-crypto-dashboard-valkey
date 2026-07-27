# Requisitos — market-dashboard (revisão Inception)

## 1. Fonte normativa
Documento do usuário: `prompts-ai-dlc-dashboard-mercado (1).md`  
Cópia no repo: `aidlc-docs/inception/requirements/prompts-fonte-normativa.md`

Este Inception **substitui** a versão anterior (sem Celery, `/api/indicators`, tabela).

## 2. Resumo da intenção

| Dimensão | Valor |
|---|---|
| Tipo | Greenfield — dashboard de mercado BFF |
| Escopo | Angular + FastAPI + Valkey + Celery + Terraform AWS (+ CI/CD opcional) |
| Complexidade | Alta |
| Idioma do processo | Português |
| Entrega | **20 histórias** em 6 fases; uma história por vez |

## 3. Objetivo
Painel web com indicadores de criptomoedas (preço, variação %, média móvel, volatilidade).  
Angular só apresenta; lógica no BFF; Valkey = cache + série temporal + broker/result Celery; worker/beat pré-calculam; produção na AWS.

## 4. Stack
| Camada | Tecnologia |
|---|---|
| Frontend | Angular 17+ standalone, HttpClient; S3 + CloudFront em prod |
| BFF | Python 3.11, FastAPI, Uvicorn, Docker |
| Assíncrono | Celery worker + beat; Valkey como broker e result backend |
| Cache/série/broker | Valkey (redis-py); Compose local; ElastiCache na AWS |
| Fonte | CoinGecko API pública |
| Infra | Terraform: VPC, ECR, ECS Fargate, ALB, ElastiCache, S3, CloudFront |

## 5. Estrutura de pastas (obrigatória)
```text
market-dashboard/
  backend/
    main.py
    config.py
    celery_app.py
    tasks.py
    services/coingecko.py
    services/cache.py
    services/indicators.py
    services/pipeline.py
    Dockerfile
    requirements.txt
  frontend/
  infra/
    main.tf variables.tf outputs.tf
    network.tf ecr.tf elasticache.tf ecs.tf frontend.tf
  docker-compose.yml   # valkey + backend + worker + beat
```

## 6. Requisitos funcionais (por fase)

### Fase 1 — Esqueleto (H1–H4)
- RF-F1-01: Card Angular (`CardMoeda`) com campos e "—" / dados via `@Input`
- RF-F1-02: `GET /api/dashboard` mock + `DashboardService` + CORS
- RF-F1-03: Cliente CoinGecko `get_market_data(coin_id)`
- RF-F1-04: Fluxo ponta a ponta real (sem cache)

### Fase 2 — Cache (H5–H7)
- RF-F2-01: Compose Valkey+backend; wrapper cache sem negócio
- RF-F2-02: Cache-aside chave `dashboard:bitcoin:indicadores`, TTL 60s
- RF-F2-03: Header `X-Cache: HIT|MISS` + logs; opcional `?refresh=true`

### Fase 3 — Série e indicadores (H8–H10)
- RF-F3-01: Série `serie:bitcoin:precos` (últimos N)
- RF-F3-02: `media_movel` em `indicators.py`
- RF-F3-03: `volatilidade` em `indicators.py` (documentar fórmula)

### Fase 4 — Amadurecimento (H11–H13)
- RF-F4-01: Múltiplas moedas via `config.py`; lista no `/api/dashboard`
- RF-F4-02: `pipeline.py` compartilhado; Celery worker
- RF-F4-03: Celery Beat batch periódico; um único beat

### Fase 5 — AWS (H14–H19)
- RF-F5-01…06: VPC → ECR → ElastiCache → ECS (BFF+worker+beat)+ALB → S3/CloudFront → amarração SG/CORS/env
- Aviso de custo; tiers baratos; `terraform destroy` ao fim

### Fase 6 — CI/CD opcional (H20)
- RF-F6-01: Pipeline push → ECR/ECS (3 serviços) + S3/CloudFront

## 7. Contrato da API (evolutivo)
Campo base (mock H2, depois real):
```json
{
  "moeda": "bitcoin",
  "preco": 100000,
  "variacao_24h": 2.5,
  "media_movel": null,
  "volatilidade": null,
  "atualizado_em": "<ISO>"
}
```
A partir de H11: lista desses objetos. Nomes alinhados FE/BE.

## 8. Requisitos não funcionais
- RNF-01: Type hints; SRP; sem segredos hardcoded
- RNF-02: Pipeline único MISS (rota e task) — sem duplicar lógica
- RNF-03: Erros CoinGecko tratados (timeout/HTTP/formato)
- RNF-04: Custo AWS controlado (t4g.micro / Fargate mínimo; destroy)
- RNF-05: Outputs Terraform: DNS ALB, URL CDN, endpoint Valkey
- RNF-06: Extensões (herdadas até nova decisão): Security Não, Resiliency Não, PBT Sim (útil em H9–H10)

## 9. Regras de interação AI-DLC
- Plano curto + OK antes de código
- Só a história atual
- Listar arquivos + teste manual ao fim
- Infra: `plan` antes de `apply`; lembrar `destroy`

## 10. Fora de escopo global (salvo histórias que pedirem)
- Auth, WAF, HTTPS custom, multi-ambiente staging/prod
- Prometheus/métricas avançadas (H7 = header+log)
- Indicadores extras (RSI etc.)
- NAT Gateway (trade-off: Fargate em subnet pública com IP público)

## 11. Decisões que invalidam o Inception anterior
| Anterior | Novo (fonte) |
|---|---|
| Sem Celery | Celery worker + beat |
| `/api/indicators` | `/api/dashboard` |
| Tabela + botão atualizar | Cards `CardMoeda` |
| `MarketIndicatorsService` | `services/pipeline.py` |
| Compose com frontend | Compose: valkey+backend+worker+beat |
| 13 histórias / 3 unidades | **20 histórias / 6 fases (= unidades)** |
