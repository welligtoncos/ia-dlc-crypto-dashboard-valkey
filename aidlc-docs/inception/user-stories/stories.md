# Histórias de Usuário — 20 (fonte normativa)

Fonte: `prompts-fonte-normativa.md`.  
Ordem = ordem de implementação. **Uma história por vez.**

---

# Fase 1 — Esqueleto funcional (sem cache)

## H01 — App Angular com card vazio
**Como** usuário, **quero** abrir o Angular e ver a estrutura do painel (sem dados reais), **para** ter a base do frontend.

**Tarefa:** `frontend/` Angular standalone; `CardMoeda` (título, preço, variação, média móvel, volatilidade = "—"); card Bitcoin de exemplo; API URL em `environment`.

**Aceite:** `ng serve` mostra card com "—"; dados via `@Input` do pai; URL não hardcoded.

**Fora:** HTTP, cálculos.

---

## H02 — Endpoint /api/dashboard mock + service Angular
**Como** sistema, **quero** `GET /api/dashboard` mock e um service Angular, **para** FE e BFF conversarem.

**Tarefa:** FastAPI mock JSON (`moeda`, `preco`, `variacao_24h`, `media_movel`, `volatilidade`, `atualizado_em`); CORS; `DashboardService` + render no card; contrato documentado.

**Aceite:** mock no browser/curl; card com valores do endpoint; interface TS alinhada.

**Fora:** CoinGecko, Valkey, Celery, cálculo real.

---

## H03 — Integração CoinGecko
**Como** sistema, **quero** buscar preço atual na CoinGecko, **para** validar a fonte externa.

**Tarefa:** `services/coingecko.py` → `get_market_data(coin_id)` com preço e variação 24h; timeout/HTTP tratados.

**Aceite:** `get_market_data("bitcoin")` real; falhas logadas sem derrubar app; sem segredos.

**Fora:** ligar à rota; cache; cálculo.

---

## H04 — Fluxo ponta a ponta com dado real
**Como** usuário, **quero** preço e variação reais no painel, **para** fechar Angular → BFF → CoinGecko.

**Tarefa:** ligar CoinGecko à rota; MM/vol ainda null; erro 502 + estado de erro na UI.

**Aceite:** dados reais no card; falha CoinGecko → erro amigável.

**Fora:** cache/Valkey (propositadamente lento).

---

# Fase 2 — Cache (Valkey local)

## H05 — Valkey local + wrapper de cache
**Como** sistema, **quero** Valkey local e BFF conectado, **para** ter cache no dev.

**Tarefa:** Compose Valkey+backend (comentar slots worker/beat p/ H12); `cache.py` get/set/ping JSON; env em `config.py`.

**Aceite:** `docker compose up`; PING ok; wrapper sem negócio.

**Fora:** usar cache na rota; Celery.

---

## H06 — Cache-aside TTL 60s
**Como** sistema, **quero** gravar/ler resultado no Valkey (TTL 60s), **para** cache-aside.

**Tarefa:** chave `dashboard:bitcoin:indicadores`; HIT/MISS na rota.

**Aceite:** 1ª chama CoinGecko; seguintes &lt;60s do cache; TTL em config.

**Fora:** série histórica; MM/vol.

---

## H07 — Observabilidade HIT/MISS
**Como** desenvolvedor, **quero** ver HIT/MISS, **para** comprovar ganho.

**Tarefa:** header `X-Cache`; log latência; opcional `?refresh=true`.

**Aceite:** header correto; HIT mais rápido; refresh força MISS se implementado.

**Fora:** Prometheus.

---

# Fase 3 — Série e cálculos

## H08 — Série temporal de preços
**Como** sistema, **quero** acumular preços no Valkey, **para** alimentar indicadores.

**Tarefa:** no MISS gravar em `serie:bitcoin:precos` (sorted set ou list); limitar N; ler últimos N ordenados via `cache.py`.

**Aceite:** cada MISS adiciona ponto; máx N; leitura ordenada.

**Fora:** calcular indicadores.

---

## H09 — Média móvel
**Como** usuário, **quero** média móvel dos últimos N preços, **para** ver tendência.

**Tarefa:** `indicators.media_movel`; integrar no MISS; card exibe.

**Aceite:** `media_movel([100,102,101,103,104]) == 102`; poucos pontos → null / "—"; só em `indicators.py`.

**Fora:** volatilidade; gráfico.

---

## H10 — Volatilidade
**Como** usuário, **quero** volatilidade no painel, **para** ver oscilação.

**Tarefa:** `indicators.volatilidade`; documentar populacional/amostral e preços vs retornos; card completo.

**Aceite:** resultado correto em lista conhecida; poucos pontos → null.

**Fora:** RSI/bandas.

---

# Fase 4 — Amadurecimento

## H11 — Múltiplas moedas
**Como** usuário, **quero** várias moedas, **para** um painel de verdade.

**Tarefa:** lista em `config.py`; cache/série por moeda; `/api/dashboard` lista; `*ngFor` de cards.

**Aceite:** nova moeda só na config; chaves distintas; falha de uma não derruba outras.

**Fora:** filtro/ordenação UI.

---

## H12 — Celery + pipeline
**Como** sistema, **quero** worker Celery e pipeline único, **para** processamento assíncrono.

**Tarefa:** `pipeline.processar_moeda`; `celery_app.py`; `tasks.py`; serviço worker no Compose; rota MISS chama pipeline.

**Aceite:** Compose sobe valkey+backend+worker; task manual grava no Valkey; sem lógica duplicada.

**Fora:** beat/agendamento.

---

## H13 — Celery Beat (batch)
**Como** sistema, **quero** pré-cálculo periódico, **para** batch além do sob demanda.

**Tarefa:** beat + schedule; serviço beat no Compose; README reativo vs proativo; respeitar rate limit CoinGecko.

**Aceite:** atualização sozinha; dashboard majoritariamente HIT; um único beat; sob demanda como fallback.

**Fora:** filas avançadas/retries sofisticados.

---

# Fase 5 — AWS Terraform

## H14 — Terraform + VPC
**Como** operador, **quero** fundação Terraform e VPC, **para** hospedar recursos.

**Tarefa:** main/variables/outputs; network 2 AZs; Fargate público sem NAT (documentar); state S3+Dynamo ou local comentado.

**Aceite:** init/plan ok; VPC/subnets/IGW no plan; região/CIDRs variáveis.

**Fora:** ECS/ElastiCache/S3.

---

## H15 — ECR + push imagem
**Como** operador, **quero** ECR e imagem do backend, **para** Fargate (BFF/worker/beat mesma imagem).

**Tarefa:** Dockerfile multi-comando; `ecr.tf`; docs build/login/push; output URL.

**Aceite:** apply cria repo; imagem publicada; output URL.

**Fora:** CI/CD (H20).

---

## H16 — ElastiCache Valkey
**Como** operador, **quero** Valkey gerenciado, **para** cache/série/broker em prod.

**Tarefa:** `elasticache.tf` t4g.micro nó único; subnet privada; SG fechado; output endpoint.

**Aceite:** apply cria cluster; endpoint output; sem ingress público.

**Fora:** réplicas/cluster mode.

---

## H17 — ECS Fargate BFF + worker + beat
**Como** operador, **quero** três serviços Fargate, **para** API e tarefas.

**Tarefa:** cluster; BFF+ALB; worker; beat desired_count=1; env Valkey; logs CW; output DNS ALB.

**Aceite:** `/api/dashboard` via ALB; beat=1; worker/beat no mesmo Valkey.

**Fora:** HTTPS/ACM/autoscaling.

---

## H18 — Angular S3 + CloudFront
**Como** operador, **quero** FE estático no CDN, **para** servir barato.

**Tarefa:** S3 privado + CloudFront OAC + SPA fallback; docs sync/invalidate; output URL.

**Aceite:** apply; app na URL CF; bucket não público.

**Fora:** domínio custom.

---

## H19 — Amarração rede/segredos/URL
**Como** operador, **quero** ligar as peças com segurança, **para** fim a fim na AWS.

**Tarefa:** SG ElastiCache ← SG tasks; env/SSM; Angular prod → ALB; CORS CloudFront; outputs revisados.

**Aceite:** HIT/MISS + beat em prod; CORS ok; sem segredo em texto plano.

**Fora:** WAF/HTTPS custom.

---

# Fase 6 — CI/CD (opcional)

## H20 — Pipeline CI/CD
**Como** desenvolvedor, **quero** push publicando FE e BE, **para** parar deploy manual.

**Tarefa:** GitHub Actions: backend→ECR+ECS (BFF/worker/beat); frontend→S3+invalidate; OIDC preferível.

**Aceite:** push main dispara; 3 serviços atualizados; FE novo no CF.

**Fora:** staging/aprovações manuais.

---

## Resumo
| Fase | Histórias | Unidade |
|---|---|---|
| 1 Esqueleto | H01–H04 | U1 |
| 2 Cache | H05–H07 | U2 |
| 3 Série/cálculos | H08–H10 | U3 |
| 4 Amadurecimento | H11–H13 | U4 |
| 5 AWS | H14–H19 | U5 |
| 6 CI/CD | H20 | U6 (opcional) |
