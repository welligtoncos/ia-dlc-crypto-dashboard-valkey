# Requisitos — market-dashboard

## 1. Resumo da Análise de Intenção

| Dimensão | Valor |
|---|---|
| Pedido do usuário | Construir, em etapas, um dashboard de mercado cripto com padrão BFF, frontend Angular e provisionamento AWS via Terraform |
| Tipo de pedido | Novo projeto (greenfield) |
| Escopo | System-wide (BFF, cache, frontend, infra) |
| Complexidade | Moderada–Alta |
| Profundidade | Standard / Comprehensive |
| Idioma do processo | Português (obrigatório) |

### Contexto fixo (todas as tarefas)
- Frontend Angular **apenas apresenta**; toda lógica de negócio e indicadores ficam no BFF.
- Valkey armazena dados para o BFF não refazer trabalho.
- Em produção, tudo roda na AWS.
- Antes de código: plano curto da unidade + OK do usuário.
- Implementar **apenas** a história atual; não antecipar histórias futuras.
- Ao terminar: listar criados/alterados + como testar manualmente.
- Em infra: mostrar `terraform plan` esperado antes de sugerir `apply`; lembrar `terraform destroy` ao fim.

---

## 2. Stack e Estrutura

### 2.1 Stack
| Camada | Tecnologia |
|---|---|
| Frontend | Angular v17+ (standalone components, HttpClient); sem lógica de negócio |
| Backend (BFF) | Python 3.11 + FastAPI (Uvicorn), containerizado (Dockerfile) |
| Cache | Valkey via redis-py; local Docker Compose; AWS ElastiCache for Valkey |
| Fonte externa | API pública CoinGecko |
| Infra | Terraform: VPC, ECR, ECS Fargate, ALB, ElastiCache Valkey, S3, CloudFront |

### 2.2 Estrutura de pastas (obrigatória)
```text
market-dashboard/
  backend/
    main.py
    config.py
    services/coingecko.py
    services/cache.py
    services/indicators.py
    Dockerfile
    requirements.txt
  frontend/                 # ng new
    src/app/...
  infra/
    main.tf variables.tf outputs.tf
    network.tf ecr.tf elasticache.tf ecs.tf frontend.tf
  docker-compose.yml        # Valkey + backend + frontend (tudo containerizado)
```

---

## 3. Requisitos Funcionais

### RF-01 — Painel de indicadores
O sistema deve exibir, por criptomoeda, os indicadores:
- Preço atual
- Variação percentual (24h)
- Média móvel simples (SMA)
- Volatilidade

**Moedas (1ª entrega):** conjunto fixo Bitcoin (BTC), Ethereum (ETH) e Solana (SOL).

### RF-02 — Cálculos no BFF
- SMA de **7 períodos** e volatilidade como **desvio-padrão percentual dos retornos diários (janela 7)**, ambos configuráveis em `config.py`.
- **NUNCA** calcular indicadores no frontend.
- **NUNCA** colocar lógica de negócio no wrapper de cache (`services/cache.py`).
- Isolar responsabilidades: fonte externa, cache, cálculo, rotas.

### RF-03 — Cache Valkey
- Cache de respostas/séries com TTL curto (ex.: **60s** preços, **300s** histórico).
- Chaves por moeda/endpoint.
- TTLs e hosts via `config.py` / variáveis de ambiente.

### RF-04 — Resiliência à CoinGecko
Tratar falha, demora ou formato inesperado:
- Se houver cache válido ou stale: devolver dados em cache com **flag de degradação**.
- Caso contrário: HTTP **502/503** com mensagem clara.

### RF-05 — Frontend Angular
- Tabela/lista simples: moeda, preço, variação %, SMA, volatilidade + botão atualizar.
- URL base da API via `environment` (sem hardcode no componente).
- Sem autenticação (painel público de estudo).

### RF-06 — Ambiente local
`docker-compose.yml` sobe **Valkey + backend + frontend** (tudo containerizado).

### RF-07 — Fatiamento da construção
Ordem das unidades/histórias:
1. BFF + Valkey local + indicadores  
2. Frontend Angular  
3. Infra Terraform AWS  

### RF-08 — Infraestrutura AWS (estudo)
- Região default: `us-east-1`
- Variáveis para região e tamanhos; tiers mais baratos
- Outputs úteis: DNS do ALB, URL do CDN
- Sem segredos hardcoded (env / variáveis Terraform)

---

## 4. Requisitos Não Funcionais

### RNF-01 — Qualidade de código
- Type hints no Python; funções pequenas de responsabilidade única.
- Sem segredos no código.

### RNF-02 — Custo
- Projeto de estudo: recursos AWS nos tiers mais baratos; destruir ao fim (`terraform destroy`).

### RNF-03 — Testabilidade (PBT habilitado)
- Extensão **Property-Based Testing** habilitada: regras PBT são restrições bloqueantes.
- Foco especial em funções puras de indicadores e transformações de dados.

### RNF-04 — Segurança / Resiliência (extensões)
- Security Baseline: **desabilitada** (PoC/estudo).
- Resiliency Baseline: **desabilitada** (iteração rápida).
- Ainda assim vale o RF-04 (degradação com cache) como requisito funcional explícito do produto.

### RNF-05 — Idioma
- Todo o processo AI-DLC (chat, artefatos, planos, aprovações) em **português**.

---

## 5. Fora de Escopo (1ª entrega / decisões atuais)
- Autenticação de usuários
- Top dinâmico por market cap
- Market cap como indicador
- Extensões Security e Resiliency Baseline
- Recursos AWS “gigantes” ou multi-região avançada

---

## 6. Critérios de Sucesso
- BFF expõe indicadores calculados para BTC, ETH e SOL com cache Valkey.
- Frontend consome o BFF e exibe tabela + atualizar, sem lógica de negócio.
- Compose local sobe stack completa.
- Terraform provisiona stack mínima em `us-east-1` com outputs ALB/CDN.
- Construção respeita ordem das 3 unidades e regras de interação AI-DLC.

---

## 7. Decisões Registradas (perguntas)

| # | Decisão |
|---|---|
| 1 | Moedas: BTC, ETH, SOL (fixo) |
| 2 | Indicadores: preço, var% 24h, SMA, volatilidade |
| 3 | SMA 7 / volatilidade janela 7, via config |
| 4 | Cache respostas/séries com TTL curto por moeda/endpoint |
| 5 | Cache stale + flag degradação; senão 502/503 |
| 6 | Sem autenticação |
| 7 | UI: tabela + botão atualizar |
| 8 | Unidades: BFF → Frontend → Infra |
| 9 | Compose: Valkey + backend + frontend |
| 10 | AWS us-east-1, tiers baratos |
| 11 | Processo em português |
| 12 | Security Baseline: Não |
| 13 | Resiliency Baseline: Não |
| 14 | PBT: Sim (bloqueante) |
