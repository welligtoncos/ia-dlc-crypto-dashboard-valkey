# Perguntas de Verificação de Requisitos

Responda cada pergunta preenchendo a letra após a tag `[Answer]:`.
Se nenhuma opção servir, escolha a última (**Outro**) e descreva a preferência.

**Decisão de idioma (já registrada):** todo o processo AI-DLC (chat, artefatos, planos, aprovações) será em **português**. A Pergunta 11 já está respondida.

**Contexto já capturado (não precisa repetir):**
- Dashboard de criptomoedas com padrão BFF
- Stack: Angular 17+ / FastAPI + Python 3.11 / Valkey / CoinGecko / Terraform AWS
- Estrutura de pastas `market-dashboard/` conforme especificado
- Frontend só apresenta; lógica e indicadores no BFF; cache no Valkey
- Construção em etapas; plano curto + OK antes de código

---

## Pergunta 1
Quais criptomoedas o dashboard deve acompanhar na primeira entrega?

A) Conjunto fixo de estudo: Bitcoin (BTC), Ethereum (ETH) e Solana (SOL)

B) Top 5 por market cap via CoinGecko (dinâmico)

C) Lista configurável em `config.py` / variável de ambiente (comece com BTC, ETH, SOL)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 2
Qual conjunto mínimo de indicadores o BFF deve expor por moeda?

A) Preço atual, variação % (24h), média móvel simples (SMA) e volatilidade

B) Apenas preço atual e variação % (24h) na primeira história; SMA e volatilidade depois

C) Preço, variação % (24h), SMA, volatilidade e market cap

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 3
Como devem ser definidos os parâmetros de cálculo dos indicadores?

A) SMA de 7 períodos e volatilidade como desvio-padrão percentual dos retornos diários (janela 7), configuráveis em `config.py`

B) SMA de 14 períodos e volatilidade (desvio-padrão) em janela 14, configuráveis em `config.py`

C) Usar apenas campos prontos da CoinGecko quando existirem; calcular no BFF só o que faltar

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 4
Qual estratégia de cache no Valkey para a primeira entrega?

A) Cache de respostas/séries com TTL curto (ex.: 60s preços, 300s histórico), chaves por moeda/endpoint

B) Cache apenas do payload final de indicadores por moeda (TTL único, ex.: 60s)

C) Cache de histórico + indicadores derivados, com TTLs separados e documentados em `config.py`

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 5
Como o BFF deve se comportar quando a CoinGecko falhar, demorar ou retornar formato inesperado?

A) Se houver cache válido/stale, devolver dados em cache com flag de degradação; senão HTTP 502/503 com mensagem clara

B) Sempre falhar rápido (erro HTTP) sem servir cache stale; registrar o erro

C) Retornar último valor em cache indefinidamente se a API externa falhar (stale-while-error sem limite)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 6
O dashboard exige autenticação de usuários?

A) Não — painel público de estudo (sem login)

B) Sim — autenticação simples (ex.: API key no BFF)

C) Sim — autenticação completa (JWT / Cognito) já na primeira entrega

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 7
Qual deve ser o foco da interface Angular na primeira entrega útil?

A) Tabela/lista simples com moeda, preço, variação %, SMA e volatilidade + botão atualizar

B) Cards por moeda com os indicadores e polling automático

C) Apenas esqueleto do app + serviço HttpClient apontando para o BFF (UI mínima)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 8
Como deseja fatiar as histórias / unidades de trabalho na construção?

A) Ordem sugerida: (1) BFF + Valkey local + indicadores, (2) Frontend Angular, (3) Infra Terraform AWS

B) Ordem sugerida: (1) Scaffold + Docker Compose/Valkey, (2) BFF/indicadores, (3) Frontend, (4) Infra AWS

C) Uma unidade por camada técnica, mas eu definirei a ordem história a história no chat

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 9
Para o ambiente local de desenvolvimento, o que o `docker-compose.yml` deve subir?

A) Apenas Valkey; BFF e frontend rodam no host (uvicorn / ng serve)

B) Valkey + backend; frontend no host com `ng serve`

C) Valkey + backend + frontend (tudo containerizado)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: C

## Pergunta 10
Qual região AWS e postura de custo para o Terraform?

A) `us-east-1`, tiers mais baratos (estudo); variáveis para região e tamanhos; lembrar `destroy` ao fim

B) `sa-east-1` (São Paulo), tiers mais baratos; mesmas regras de custo

C) Região via variável (sem default fixo no código), tiers mais baratos

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 11
Idioma do processo AI-DLC (chat, artefatos, planos, aprovações)?

A) Português (todo o processo)

B) Inglês

C) Português nos artefatos de inception; código/comentários em inglês

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

---

# Extensões (opt-in)

## Pergunta 12 — Security Baseline
Devem ser aplicadas regras da extensão **Security Baseline** neste projeto?

A) Sim — aplicar regras de SECURITY como restrições bloqueantes (recomendado para apps production-grade)

B) Não — pular regras de SECURITY (adequado para PoC / projeto de estudo)

X) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: B

## Pergunta 13 — Resiliency Baseline
Deve ser aplicada a extensão **Resiliency Baseline** neste projeto?

**O que é.** Boas práticas direcionais de design (Well-Architected Reliability) para tolerância a falhas, observabilidade e recuperação — ponto de partida, não certificação de produção.

**O que NÃO é.** Não torna o workload production-ready nem garante RTO/RPO.

A) Sim — aplicar como orientação de design (recomendado como ponto de partida para workloads importantes)

B) Não — pular (adequado para PoC / estudo com iteração rápida)

X) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: B

## Pergunta 14 — Property-Based Testing
Devem ser aplicadas regras de **Property-Based Testing (PBT)**?

A) Sim — aplicar PBT como restrição (recomendado quando há lógica de negócio / transformações)

B) Parcial — PBT só para funções puras e round-trips de serialização (ex.: cálculos em `indicators.py`)

C) Não — pular PBT

X) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A
