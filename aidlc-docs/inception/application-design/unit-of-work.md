# Unidades de Trabalho — revisão (6 fases)

Código em `market-dashboard/` (backend, frontend, infra, docker-compose.yml).

## U1 — Fase 1 Esqueleto (H01–H04)
Angular card + BFF mock + CoinGecko + ponta a ponta sem cache.  
Compose ainda não obrigatório (H05). FE via `ng serve`; BE via uvicorn.

## U2 — Fase 2 Cache (H05–H07)
Compose Valkey+backend; cache-aside TTL 60s; X-Cache.

## U3 — Fase 3 Série/cálculos (H08–H10)
Série temporal; média móvel; volatilidade; PBT recomendado nos puros.

## U4 — Fase 4 Amadurecimento (H11–H13)
Multi-moedas; pipeline + Celery worker; Celery Beat.

## U5 — Fase 5 AWS (H14–H19)
Terraform VPC→ECR→ElastiCache→ECS×3+ALB→S3/CF→amarração.  
Sempre `plan` antes de `apply`; `destroy` ao fim.

## U6 — Fase 6 CI/CD (H20) — opcional
GitHub Actions deploy BE+FE.

## Sequência
U1 → U2 → U3 → U4 → U5 → (U6 opcional).  
Dentro de cada unidade: histórias na ordem numérica.
