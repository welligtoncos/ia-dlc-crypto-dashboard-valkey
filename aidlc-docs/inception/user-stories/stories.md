# Histórias de Usuário — market-dashboard

**Persona**: Visitante do Painel (única)  
**Organização**: 3 épicos (BFF → Frontend → Infra), histórias pequenas  
**Formato**: “Como…, quero…, para…” + critérios Given/When/Then  
**Enablers técnicos**: Visitante como beneficiário  

---

## Épico E1 — BFF + ambiente local

### US-BFF-01 — Stack local containerizada
**Como** Visitante do Painel,  
**quero** que a stack local (Valkey, backend e frontend) suba de forma reproduzível via Docker Compose,  
**para** que o painel e a API estejam disponíveis para consulta em ambiente de estudo.

**Persona**: Visitante do Painel  
**Épico**: E1

**Critérios de aceite**
1. **Dado** o repositório com `docker-compose.yml`, **quando** executo `docker compose up`, **então** sobem os serviços Valkey, backend e frontend sem segredos hardcoded.
2. **Dado** a stack no ar, **quando** verifico a saúde dos serviços, **então** o backend responde e o frontend fica acessível na porta configurada.
3. **Dado** a necessidade de derrubar o ambiente, **quando** executo `docker compose down`, **então** os containers são encerrados de forma limpa.

---

### US-BFF-02 — Configuração do BFF
**Como** Visitante do Painel,  
**quero** que TTLs, moedas, URLs e host do Valkey venham de configuração/ambiente,  
**para** que o painel funcione em local e AWS sem valores sensíveis no código.

**Persona**: Visitante do Painel  
**Épico**: E1

**Critérios de aceite**
1. **Dado** variáveis de ambiente (ou defaults seguros em `config.py`), **quando** o BFF inicia, **então** carrega TTL de preços/histórico, lista BTC/ETH/SOL, URL CoinGecko e host Valkey.
2. **Dado** o código-fonte, **quando** inspeciono o repositório, **então** não há segredos hardcoded.
3. **Dado** a ausência de uma variável obrigatória crítica, **quando** o BFF sobe, **então** falha com mensagem clara (ou usa default documentado, se aplicável).

---

### US-BFF-03 — Cliente CoinGecko
**Como** Visitante do Painel,  
**quero** que o BFF obtenha dados de preço/histórico da CoinGecko de forma isolada,  
**para** que falhas da fonte externa não quebrem o restante da aplicação de forma opaca.

**Persona**: Visitante do Painel  
**Épico**: E1

**Critérios de aceite**
1. **Dado** a CoinGecko disponível, **quando** o cliente solicita preço ou série para BTC/ETH/SOL, **então** retorna dados tipados/estruturados para o restante do BFF.
2. **Dado** timeout ou erro HTTP da CoinGecko, **quando** a chamada falha, **então** o cliente propaga erro tratável (sem engolir silenciosamente).
3. **Dado** payload com formato inesperado, **quando** o cliente faz o parse, **então** sinaliza erro de formato sem derrubar o processo inteiro.

---

### US-BFF-04 — Wrapper de cache Valkey
**Como** Visitante do Painel,  
**quero** que respostas/séries fiquem em cache no Valkey com TTL curto,  
**para** que consultas seguintes ao painel sejam rápidas e evitem refetch desnecessário.

**Persona**: Visitante do Painel  
**Épico**: E1

**Critérios de aceite**
1. **Dado** uma chave por moeda/endpoint, **quando** gravo um valor com TTL (ex.: 60s preços, 300s histórico), **então** consigo ler o valor enquanto o TTL for válido.
2. **Dado** o TTL expirado, **quando** leio a chave, **então** o cache indica ausência (miss).
3. **Dado** o módulo `cache.py`, **quando** reviso responsabilidades, **então** não há cálculo de indicadores nem regra de negócio — apenas get/set/delete (ou equivalente).

---

### US-BFF-05 — Cálculo de indicadores
**Como** Visitante do Painel,  
**quero** variação % (24h), SMA(7) e volatilidade (janela 7) calculados no BFF,  
**para** ver indicadores consistentes sem lógica no frontend.

**Persona**: Visitante do Painel  
**Épico**: E1

**Critérios de aceite**
1. **Dado** uma série de preços diários suficiente, **quando** calculo SMA de 7 períodos, **então** o resultado é a média aritmética dos últimos 7 valores.
2. **Dado** a mesma série, **quando** calculo volatilidade, **então** obtenho o desvio-padrão percentual dos retornos diários na janela 7 (parâmetros via `config.py`).
3. **Dado** preço atual e referência 24h, **quando** calculo variação %, **então** o percentual reflete a mudança no período.
4. **Dado** série insuficiente para a janela, **quando** tento calcular, **então** o serviço sinaliza erro/indisponibilidade do indicador de forma explícita.
5. **Dado** PBT habilitado, **quando** os testes de propriedades forem criados na construção, **então** funções puras de indicadores serão cobertas por propriedades (invariantes/oráculos conforme design).

---

### US-BFF-06 — API de indicadores com cache e degradação
**Como** Visitante do Painel,  
**quero** um endpoint do BFF que devolva preço, variação %, SMA e volatilidade para BTC/ETH/SOL,  
**para** que o painel consuma um contrato estável já com cache e fallback.

**Persona**: Visitante do Painel  
**Épico**: E1

**Critérios de aceite**
1. **Dado** CoinGecko e Valkey saudáveis (cache miss), **quando** chamo o endpoint de indicadores, **então** recebo os quatro indicadores por moeda e o resultado intermediário/final é cacheado.
2. **Dado** cache hit válido, **quando** chamo o endpoint novamente dentro do TTL, **então** a resposta vem do Valkey sem refetch desnecessário à CoinGecko.
3. **Dado** CoinGecko falha/demora/formato inválido e existe cache stale, **quando** chamo o endpoint, **então** recebo os dados em cache com **flag de degradação**.
4. **Dado** CoinGecko falha e não há cache, **quando** chamo o endpoint, **então** recebo HTTP 502 ou 503 com mensagem clara.
5. **Dado** o frontend (ou cliente HTTP), **quando** consome a API, **então** não precisa calcular nenhum indicador.

---

## Épico E2 — Frontend Angular

### US-FE-01 — App Angular e environment
**Como** Visitante do Painel,  
**quero** um app Angular (standalone) com a URL base da API em environment,  
**para** abrir o painel apontando ao BFF sem URLs fixas nos componentes.

**Persona**: Visitante do Painel  
**Épico**: E2

**Critérios de aceite**
1. **Dado** o projeto Angular v17+ com standalone components, **quando** inicio a aplicação, **então** ela sobe sem erros de bootstrap.
2. **Dado** o arquivo de environment, **quando** o app lê a configuração, **então** obtém a URL base da API.
3. **Dado** um componente de UI, **quando** inspeciono o código, **então** não há URL da API hardcoded.

---

### US-FE-02 — Serviço HttpClient do BFF
**Como** Visitante do Painel,  
**quero** um serviço Angular que busque os indicadores no BFF via HttpClient,  
**para** a interface obter dados prontos sem regras de negócio no cliente.

**Persona**: Visitante do Painel  
**Épico**: E2

**Critérios de aceite**
1. **Dado** o BFF disponível, **quando** o serviço solicita indicadores, **então** retorna o payload tipado/estruturado para a UI.
2. **Dado** erro HTTP do BFF (ex.: 502/503), **quando** o serviço trata a resposta, **então** propaga/estado de erro consumível pela UI (sem calcular indicadores).
3. **Dado** o código do serviço, **quando** reviso responsabilidades, **então** não há SMA, volatilidade nem variação calculadas no frontend.

---

### US-FE-03 — Tabela de indicadores e atualizar
**Como** Visitante do Painel,  
**quero** uma tabela com moeda, preço, variação %, SMA e volatilidade e um botão atualizar,  
**para** consultar e refrescar os indicadores sob demanda.

**Persona**: Visitante do Painel  
**Épico**: E2

**Critérios de aceite**
1. **Dado** o BFF retornando dados de BTC/ETH/SOL, **quando** abro o painel, **então** vejo uma linha (ou equivalente) por moeda com os quatro indicadores.
2. **Dado** a tabela visível, **quando** clico em atualizar, **então** uma nova chamada ao BFF atualiza os valores exibidos.
3. **Dado** resposta com flag de degradação, **quando** a UI renderiza, **então** mostro um aviso visível de que os dados podem estar desatualizados/degradados.
4. **Dado** erro sem dados, **quando** a UI renderiza, **então** mostro mensagem de erro clara (sem inventar números).

---

## Épico E3 — Infraestrutura AWS (Terraform)

### US-INF-01 — Rede VPC
**Como** Visitante do Painel,  
**quero** que a base de rede AWS (VPC e subnets) exista via Terraform com tiers baratos,  
**para** que os serviços do painel tenham onde rodar em `us-east-1`.

**Persona**: Visitante do Painel  
**Épico**: E3

**Critérios de aceite**
1. **Dado** variáveis de região/tamanho, **quando** aplico o módulo de rede, **então** a VPC e subnets necessárias são criadas em `us-east-1` (ou região variável).
2. **Dado** o código Terraform, **quando** reviso recursos, **então** não há dimensionamento “gigante” — apenas o mínimo de estudo.
3. **Dado** `terraform plan`, **quando** analiso a saída esperada, **então** vejo criação dos recursos de rede previstos (antes de qualquer `apply`).

---

### US-INF-02 — ElastiCache for Valkey
**Como** Visitante do Painel,  
**quero** um Valkey gerenciado (ElastiCache) provisionado via Terraform,  
**para** que o BFF em AWS use o mesmo padrão de cache do ambiente local.

**Persona**: Visitante do Painel  
**Épico**: E3

**Critérios de aceite**
1. **Dado** a VPC existente, **quando** aplico o recurso ElastiCache Valkey (tier barato), **então** o endpoint fica disponível para o BFF.
2. **Dado** outputs Terraform, **quando** consulto a saída, **então** obtenho informações úteis de conexão (sem expor segredos no código).
3. **Dado** o fim do estudo, **quando** executo `terraform destroy`, **então** o recurso pode ser destruído com o restante da stack.

---

### US-INF-03 — ECR, ECS Fargate e ALB
**Como** Visitante do Painel,  
**quero** o BFF publicado em ECS Fargate atrás de um ALB (imagem no ECR),  
**para** acessar a API de indicadores pela internet de forma mínima e barata.

**Persona**: Visitante do Painel  
**Épico**: E3

**Critérios de aceite**
1. **Dado** Dockerfile do backend, **quando** a imagem é publicada no ECR e o serviço ECS sobe, **então** o ALB encaminha tráfego ao BFF.
2. **Dado** outputs Terraform, **quando** consulto a saída, **então** obtenho o DNS do ALB.
3. **Dado** `terraform plan` da unidade, **quando** reviso, **então** vejo ECR/ECS/ALB nos tamanhos mínimos configuráveis por variáveis.
4. **Dado** o fim do estudo, **quando** uso `terraform destroy`, **então** esses recursos entram no ciclo de destruição.

---

### US-INF-04 — Frontend estático em S3 e CloudFront
**Como** Visitante do Painel,  
**quero** o frontend Angular servido via S3 + CloudFront,  
**para** abrir o painel pela URL do CDN.

**Persona**: Visitante do Painel  
**Épico**: E3

**Critérios de aceite**
1. **Dado** o build do Angular, **quando** o bucket S3 e a distribuição CloudFront são provisionados, **então** o painel fica acessível pela URL do CDN.
2. **Dado** outputs Terraform, **quando** consulto a saída, **então** obtenho a URL do CDN.
3. **Dado** a configuração do frontend em AWS, **quando** o app chama a API, **então** usa a URL do BFF/ALB via environment de produção (sem hardcode no componente).
4. **Dado** o fim do estudo, **quando** executo `terraform destroy`, **então** S3/CloudFront podem ser destruídos com a stack.

---

## Mapeamento Persona ↔ Histórias

| Persona | Histórias |
|---|---|
| Visitante do Painel | Todas (US-BFF-01…06, US-FE-01…03, US-INF-01…04) |

## Ordem de implementação sugerida
1. US-BFF-01 → US-BFF-02 → US-BFF-03 → US-BFF-04 → US-BFF-05 → US-BFF-06  
2. US-FE-01 → US-FE-02 → US-FE-03  
3. US-INF-01 → US-INF-02 → US-INF-03 → US-INF-04  

## Cobertura de requisitos (referência)
| Requisito | Histórias |
|---|---|
| RF-01, RF-02 | US-BFF-05, US-BFF-06, US-FE-03 |
| RF-03 | US-BFF-04, US-BFF-06 |
| RF-04 | US-BFF-03, US-BFF-06, US-FE-03 |
| RF-05 | US-FE-01…03 |
| RF-06 | US-BFF-01 |
| RF-07 | Ordem dos épicos |
| RF-08 | US-INF-01…04 |
| RNF-03 (PBT) | US-BFF-05 (na construção) |
