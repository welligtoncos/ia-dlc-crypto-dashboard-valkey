# Mapa Histórias → Unidades

## Visão geral

| Unidade | Épico | Histórias |
|---|---|---|
| U1 | E1 BFF + local | US-BFF-01 … US-BFF-06 |
| U2 | E2 Frontend | US-FE-01 … US-FE-03 |
| U3 | E3 Infra | US-INF-01 … US-INF-04 |

**Cobertura**: 13/13 histórias atribuídas. Nenhuma história órfã.

---

## U1 — checklist de implementação

| Ordem | História | Resumo |
|---|---|---|
| 1 | US-BFF-01 | Stack local Compose (Valkey+backend+frontend) |
| 2 | US-BFF-02 | Configuração BFF (env/config.py) |
| 3 | US-BFF-03 | Cliente CoinGecko |
| 4 | US-BFF-04 | Wrapper cache Valkey |
| 5 | US-BFF-05 | Cálculo de indicadores (+ PBT na construção) |
| 6 | US-BFF-06 | API indicadores com cache e degradação |

## U2 — checklist de implementação

| Ordem | História | Resumo |
|---|---|---|
| 1 | US-FE-01 | App Angular + environment |
| 2 | US-FE-02 | Serviço HttpClient |
| 3 | US-FE-03 | Tabela + atualizar + degradação UI |

## U3 — checklist de implementação

| Ordem | História | Resumo |
|---|---|---|
| 1 | US-INF-01 | Rede VPC |
| 2 | US-INF-02 | ElastiCache Valkey |
| 3 | US-INF-03 | ECR + ECS Fargate + ALB |
| 4 | US-INF-04 | S3 + CloudFront |

---

## Persona
Todas as histórias: **Visitante do Painel** (beneficiário).
