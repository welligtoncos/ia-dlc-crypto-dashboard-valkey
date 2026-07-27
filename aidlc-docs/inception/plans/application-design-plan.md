# Plano de Design da Aplicação — market-dashboard

**Status**: Parte 2 — Artefatos gerados e aprovados (usuário solicitou seguir para Geração de Unidades)  
**Base**: requirements.md + stories.md + execution-plan.md  
**Idioma**: Português

### Decisões consolidadas
| Tema | Decisão |
|---|---|
| Componentes BFF | MarketDataSource, CacheStore, IndicatorsEngine, MarketIndicatorsService (+ rotas finas) |
| Orquestração | `MarketIndicatorsService` (P3 ajustado para B / esclarecimento B) |
| API | `GET /api/indicators` agregado com `degraded` |
| Frontend | `MarketApiService` + `DashboardComponent` |
| Degradação UI | Banner global + marca por linha (se houver granularidade) |
| Infra no design | Componentes lógicos: Network, CacheManaged, BffRuntime, FrontendCdn |
| Dependências | cache ⟂ indicators; só o orquestrador combina; FE só HTTP do BFF |
| Métodos | Assinaturas tipadas de alto nível (sem regras detalhadas de cálculo) |

## Instruções
Preencha cada `[Answer]:` com a letra. Se escolher **Outro**, descreva após a tag.  
Após respostas + aprovação deste plano, serão gerados os artefatos em `aidlc-docs/inception/application-design/`.

---

## Contexto já fixo (não precisa repetir)
- Padrão BFF: Angular só apresenta; lógica no FastAPI
- Isolamento: `coingecko.py` | `cache.py` | `indicators.py` | rotas em `main.py`
- Cache Valkey sem lógica de negócio
- Compose: Valkey + backend + frontend
- Infra Terraform: VPC, ECR, ECS/ALB, ElastiCache, S3/CloudFront

---

## Perguntas de Design

## Pergunta 1 — Fronteiras dos componentes do BFF
Como modelar os componentes do backend no design?

A) Quatro componentes espelhando arquivos: CoinGeckoClient, CacheStore, IndicatorsEngine, ApiRoutes (orquestração nas rotas/main)

B) Três serviços de domínio + um Application Service: MarketDataSource, CacheStore, IndicatorsEngine, MarketIndicatorsService (orquestra e é chamado pelas rotas)

C) Um único componente BFF monolítico no design (detalhes internos só na construção)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: B

## Pergunta 2 — Contrato da API de indicadores
Qual forma de endpoint o design deve assumir?

A) `GET /api/indicators` retornando lista de BTC/ETH/SOL com preço, var%, SMA, volatilidade e flag `degraded`

B) `GET /api/indicators/{coin_id}` por moeda + `GET /api/indicators` agregador opcional

C) `GET /health` + `GET /api/market/summary` (nome alternativo, mesmo payload agregado)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 3 — Orquestração (quem chama quem)
Onde fica a orquestração cache → CoinGecko → indicadores?

A) Nas rotas FastAPI (`main.py`): rota decide cache hit/miss, chama cliente, calcula, grava cache

B) Em um Application Service dedicado (ex.: `MarketIndicatorsService`) chamado pelas rotas; rotas só HTTP

C) Nos próprios services, com IndicatorsEngine coordenando cache e CoinGecko

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 4 — Componentes do Frontend
Como decompor o Angular no design?

A) Três peças: `AppShell`, `MarketApiService` (HttpClient), `IndicatorsTableComponent` (tabela + botão atualizar + aviso de degradação)

B) Duas peças: `MarketApiService` + um único `DashboardComponent` (tudo na tela)

C) Incluir também um `IndicatorsStore`/estado simples (signal/service) entre API e tabela

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: B

## Pergunta 5 — Tratamento de degradação na UI
Como o frontend deve representar `degraded`?

A) Banner/aviso global na página da tabela quando qualquer moeda (ou o payload) vier degradado

B) Indicador por linha da tabela (badge/ícone na moeda afetada)

C) Ambos: banner global + marca por linha se o contrato trouxer granularidade

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: C

## Pergunta 6 — Componentes de Infra no design de aplicação
Até onde o Design da Aplicação deve descrever a infra?

A) Componentes lógicos de deploy: Network, CacheManaged, BffRuntime, FrontendCdn — só responsabilidades e dependências (detalhe Terraform na U3)

B) Apenas mencionar “Infra AWS” como caixa única; detalhar tudo só no Design de Infraestrutura (U3)

C) Espelhar arquivos Terraform (`network`, `elasticache`, `ecs`, `frontend`) como componentes com inputs/outputs de alto nível

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 7 — Dependências e acoplamento
Qual regra de dependência deve prevalecer?

A) `cache` e `indicators` não dependem um do outro; só o orquestrador (rotas ou application service) os combina. Frontend depende só do contrato HTTP do BFF

B) `indicators` pode ler do cache diretamente; CoinGecko só via orquestrador

C) Frontend pode, no futuro, chamar CoinGecko — design deve deixar isso aberto

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 8 — Nível de detalhe das assinaturas de métodos
O que incluir em `component-methods.md`?

A) Assinaturas Python/TypeScript de alto nível (nome, params tipados, retorno) sem regras de cálculo detalhadas

B) Apenas lista de métodos com propósito em uma linha (sem tipos)

C) Assinaturas + esboço de DTOs/JSON do endpoint de indicadores

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

---

## Checklist de geração (após aprovação deste plano)

- [x] Gerar `components.md` — componentes e responsabilidades
- [x] Gerar `component-methods.md` — assinaturas de alto nível
- [x] Gerar `services.md` — serviços e orquestração
- [x] Gerar `component-dependency.md` — matriz e fluxos
- [x] Gerar `application-design.md` — consolidação
- [x] Validar consistência com requisitos, histórias e estrutura de pastas
- [x] Atualizar `aidlc-state.md` e `audit.md`
- [x] Apresentar design para aprovação explícita

## Artefatos obrigatórios
- [x] `components.md`
- [x] `component-methods.md`
- [x] `services.md`
- [x] `component-dependency.md`
- [x] `application-design.md`
