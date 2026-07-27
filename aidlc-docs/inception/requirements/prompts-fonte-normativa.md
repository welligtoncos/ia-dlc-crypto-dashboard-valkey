# Prompts AI-DLC — Dashboard de Mercado (Angular + BFF + Valkey + Celery na AWS)

Cada bloco é uma **unidade de trabalho** pronta para colar no seu agente de IA
(Claude Code, Cursor, Amazon Q, Copilot). Rode uma história por vez, valide o resultado e
só então avance. Cole o **Prompt Base** primeiro (ou salve-o como arquivo de regras do
projeto) — ele dá o contexto que todos os demais assumem.

> Princípio AI-DLC: a IA rende com especificidade. Não remova os critérios de aceite nem a
> seção "Fora de escopo" — são eles que impedem o agente de fazer mais do que a história pede.

---

## ⚠️ Aviso de custo (leia antes da Fase 5)

As fases 1–4 rodam de graça na sua máquina (Docker). A partir da Fase 5 você sobe recursos
reais na AWS. ElastiCache, Application Load Balancer e Fargate **cobram por hora enquanto
estão ligados** e não cabem confortavelmente no free tier. Para estudar sem susto na fatura:
use os tamanhos mais baratos (t4g.micro / Fargate mínimo) e rode `terraform destroy` ao
terminar cada sessão. Suba, teste, derrube.

---

## Stack

- **Frontend:** Angular (standalone components, v17+), servido como estático via S3 + CloudFront
- **Backend / BFF:** Python 3.11 + FastAPI + Uvicorn, containerizado, rodando em ECS Fargate
- **Processamento assíncrono:** Celery (worker + beat), usando o Valkey como broker e backend
- **Cache / série temporal / broker:** Valkey — local via Docker Compose; na AWS via ElastiCache for Valkey
- **Fonte externa:** API pública da CoinGecko
- **Infraestrutura:** Terraform (VPC, ECR, ECS/Fargate, ALB, ElastiCache, S3, CloudFront)
- **Dev local:** Docker Compose (Valkey + backend + worker + beat)

O Valkey acumula três papéis: cache de resultado, store da série temporal e broker/result
backend do Celery. Arquitetura na nuvem: o navegador carrega o Angular do CloudFront; o
Angular chama o BFF pelo DNS do ALB; o BFF (task Fargate) fala com a CoinGecko e o ElastiCache;
um worker Celery (outra task Fargate) executa as tarefas agendadas pelo beat.

---

## Prompt Base (cole isto primeiro, sempre)

```
Você vai me ajudar a construir, em etapas, um dashboard de mercado com padrão BFF
(Backend for Frontend): frontend Angular, processamento assíncrono com Celery e
provisionamento na AWS via Terraform. Contexto e regras que valem para TODAS as tarefas:

OBJETIVO DO PROJETO
Um painel web que mostra indicadores de criptomoedas (preço, variação %, média móvel,
volatilidade). O frontend Angular só apresenta; toda lógica fica no BFF; o Valkey guarda
dados e serve de broker do Celery; tarefas periódicas rodam em worker Celery. Em produção,
tudo roda na AWS.

STACK
- Frontend: Angular v17+ com standalone components e HttpClient. Sem lógica de negócio.
- Backend: Python 3.11 + FastAPI (Uvicorn), containerizado (Dockerfile).
- Assíncrono: Celery (worker + beat) com Valkey como broker e result backend.
- Cache/série/broker: Valkey via redis-py. Local: Docker Compose. AWS: ElastiCache for Valkey.
- Fonte externa: API pública da CoinGecko.
- Infra: Terraform (VPC, ECR, ECS Fargate, ALB, ElastiCache for Valkey, S3, CloudFront).

ESTRUTURA DE PASTAS (respeite-a)
market-dashboard/
  backend/
    main.py                 # app FastAPI + rotas
    config.py               # TTL, moedas, URLs, host do Valkey e do broker (via env)
    celery_app.py           # instância do Celery (broker/backend = Valkey)
    tasks.py                # tarefas Celery (coleta + cálculo + gravação)
    services/coingecko.py   # cliente da API externa
    services/cache.py       # wrapper do Valkey (redis-py)
    services/indicators.py  # cálculos (variação, média móvel, volatilidade)
    services/pipeline.py    # caminho de MISS compartilhado (rota E task usam)
    Dockerfile
    requirements.txt
  frontend/                 # projeto Angular (ng new)
    src/app/...
  infra/                    # Terraform
    main.tf variables.tf outputs.tf
    network.tf ecr.tf elasticache.tf ecs.tf frontend.tf
  docker-compose.yml        # dev local: valkey + backend + worker + beat

CONVENÇÕES
- Type hints no Python; funções pequenas de responsabilidade única.
- NUNCA calcule indicadores no frontend. NUNCA coloque lógica de negócio no wrapper de cache.
- Isole responsabilidades por arquivo (fonte externa, cache, cálculo, rotas, tarefas).
- O caminho "coleta → calcula → grava" mora em services/pipeline.py e é chamado tanto pela
  rota (no MISS) quanto pela task Celery. Não duplique essa lógica.
- Trate erros da fonte externa: ela pode falhar, demorar ou mudar de formato.
- Sem segredos hardcoded; use variáveis de ambiente / config.py / variáveis do Terraform.
- No Angular, a URL base da API vem de environment (não hardcode no componente).
- No Terraform: variáveis para região e tamanhos; use tiers baratos (projeto de estudo);
  exponha outputs úteis (DNS do ALB, URL do CDN, endpoint do Valkey).

REGRAS DE INTERAÇÃO (AI-DLC)
- Antes de escrever código, apresente um plano curto da unidade de trabalho e aguarde meu OK.
- Implemente APENAS a história atual. Não antecipe funcionalidades de histórias futuras.
- Ao terminar, liste o que criou/alterou e como eu testo manualmente.
- Em histórias de infra, mostre o `terraform plan` esperado antes de sugerir `apply`, e
  lembre-me de `terraform destroy` ao fim.

Responda "Contexto carregado" e aguarde a primeira história.
```

---

# Fase 1 — Esqueleto funcional (sem cache)

## História 1 — App Angular com card vazio

```
HISTÓRIA
Como usuário, quero abrir a aplicação Angular e ver a estrutura de um painel de mercado
(ainda sem dados reais), para ter a base do frontend funcionando.

TAREFA
Inicialize um projeto Angular em frontend/ (standalone components). Crie um componente
CardMoeda que exibe título, preço, variação, média móvel e volatilidade, todos com "—".
Renderize um card de exemplo (Bitcoin) na tela inicial. Defina a URL base da API em
src/environments (apontando para http://localhost:8000 por enquanto).

CRITÉRIOS DE ACEITE
- `ng serve` sobe a app e mostra o card com os quatro campos rotulados exibindo "—".
- O CardMoeda recebe os dados via @Input a partir de um objeto de exemplo no componente pai.
- A URL da API está em environment.ts, não hardcoded no componente.

FORA DE ESCOPO
- Nenhuma chamada HTTP ainda. Nenhum cálculo.

DEFINIÇÃO DE PRONTO
`ng serve` mostra o card renderizado a partir do objeto de exemplo.
```

## História 2 — Endpoint /api/dashboard com mock + service Angular

```
HISTÓRIA
Como sistema, quero um endpoint GET /api/dashboard devolvendo dado mockado e um service
Angular que o consome, para frontend e BFF conversarem antes de integrar a fonte externa.

TAREFA
Backend: crie backend/main.py (FastAPI) com GET /api/dashboard retornando JSON mockado:
{ "moeda":"bitcoin","preco":100000,"variacao_24h":2.5,
  "media_movel":null,"volatilidade":null,"atualizado_em":"<ISO>" }
Habilite CORS para o dev server do Angular. Crie requirements.txt (fastapi, uvicorn).
Frontend: crie um DashboardService (HttpClient) que chama /api/dashboard e um fluxo que
renderiza o CardMoeda com a resposta.

CRITÉRIOS DE ACEITE
- Subir o backend e acessar /api/dashboard devolve o JSON mockado.
- Com backend + `ng serve` rodando, o card exibe os valores vindos do endpoint.
- O contrato (nomes dos campos) está documentado em comentário no topo de main.py e refletido
  numa interface TypeScript no frontend.

FORA DE ESCOPO
- Sem CoinGecko, sem Valkey, sem Celery, sem cálculo real ainda.

DEFINIÇÃO DE PRONTO
O Angular busca o dado (mockado) do backend e o exibe.
```

## História 3 — Integração com a CoinGecko

```
HISTÓRIA
Como sistema, quero buscar o preço atual de uma moeda na CoinGecko, para validar a
integração com a fonte externa.

TAREFA
Crie backend/services/coingecko.py com get_market_data(coin_id: str) que chama a API pública
da CoinGecko e retorna preço atual e variação de 24h. Consulte a documentação ATUAL da
CoinGecko para o endpoint correto e para os limites de requisição do plano gratuito. Trate
timeout e erro HTTP retornando erro claro, sem estourar exceção crua.

CRITÉRIOS DE ACEITE
- get_market_data("bitcoin") retorna dict com preco e variacao_24h reais.
- Falha de rede ou status != 200 é tratada e logada, sem derrubar a app.
- Nenhuma chave secreta hardcoded.

FORA DE ESCOPO
- Não ligar à rota ainda (próxima história). Sem cache, sem cálculo.

DEFINIÇÃO DE PRONTO
Teste manual mostra a função retornando dados reais da CoinGecko.
```

## História 4 — Fluxo ponta a ponta com dado real

```
HISTÓRIA
Como usuário, quero ver preço e variação de 24h reais no painel, fechando o primeiro fluxo
completo Angular → BFF → fonte externa.

TAREFA
Ligue services/coingecko.py à rota GET /api/dashboard. A rota chama a CoinGecko a cada
request, monta o JSON no contrato (média móvel e volatilidade ainda null) e devolve. O
Angular já renderiza; ajuste o que for preciso e trate o estado de erro na UI.

CRITÉRIOS DE ACEITE
- /api/dashboard devolve preço e variação reais; o card os exibe.
- Se a CoinGecko falhar, a rota devolve erro amigável (ex: 502) e o Angular mostra estado de
  erro em vez de quebrar.

FORA DE ESCOPO
- Sem cache — é intencional que cada request bata na API. NÃO adicione Valkey aqui.

DEFINIÇÃO DE PRONTO
O painel mostra dados reais, ponta a ponta. (Vai estar lento — de propósito.)
```

---

# Fase 2 — Cache do resultado (Valkey local)

## História 5 — Valkey local + wrapper de cache

```
HISTÓRIA
Como sistema, quero rodar o Valkey localmente e conectar o BFF a ele, para ter a
infraestrutura de cache no ambiente de desenvolvimento.

TAREFA
Crie docker-compose.yml subindo Valkey (imagem valkey/valkey) e o backend. Deixe o compose
preparado para receber, mais adiante, os serviços de worker e beat do Celery (comente onde
eles entrarão — serão adicionados na História 12). Crie backend/services/cache.py: wrapper
fino sobre redis-py com get(chave), set(chave, valor, ttl) e um ping de conexão; serializa/
desserializa JSON transparentemente. Host/porta vêm de variáveis de ambiente (config.py).
Adicione redis ao requirements.txt.

CRITÉRIOS DE ACEITE
- `docker compose up` sobe Valkey + backend.
- Um healthcheck (endpoint ou log) confirma que o BFF fala com o Valkey (PING).
- O wrapper não contém lógica de negócio nem de cálculo.

FORA DE ESCOPO
- Ainda NÃO usar o cache na rota (próxima história). Ainda NÃO adicionar Celery.

DEFINIÇÃO DE PRONTO
Subo tudo com Docker Compose e confirmo a conexão BFF ↔ Valkey.
```

## História 6 — Cache-aside com TTL de 60s

```
HISTÓRIA
Como sistema, quero gravar o resultado no Valkey com TTL de 60s e lê-lo antes de recalcular,
implementando o padrão cache-aside.

TAREFA
Na rota GET /api/dashboard: monte a chave "dashboard:bitcoin:indicadores"; tente ler do
Valkey (HIT → retorna cacheado); no MISS, busque na CoinGecko, monte o JSON, grave com
TTL=60s (constante em config.py) e retorne.

CRITÉRIOS DE ACEITE
- 1ª chamada após expirar bate na CoinGecko; as seguintes (<60s) voltam do cache sem chamar
  a API externa.
- O TTL é constante configurável em config.py.
- Após 60s, nova chamada busca dados frescos.

FORA DE ESCOPO
- Sem série histórica e sem média móvel/volatilidade ainda.

DEFINIÇÃO DE PRONTO
Chamadas repetidas em menos de 60s não geram tráfego novo para a CoinGecko.
```

## História 7 — Observabilidade de HIT/MISS

```
HISTÓRIA
Como desenvolvedor, quero enxergar quando a resposta veio de cache (HIT) ou foi recalculada
(MISS), para comprovar o ganho e medir a latência.

TAREFA
Adicione cabeçalho "X-Cache: HIT|MISS" na resposta e um log por request com origem e tempo
em ms. Opcional: ?refresh=true força MISS ignorando o cache.

CRITÉRIOS DE ACEITE
- A resposta traz X-Cache correto.
- Os logs mostram a latência; HIT é visivelmente mais rápido que MISS.
- Se implementado, ?refresh=true sempre recalcula e regrava.

FORA DE ESCOPO
- Sem Prometheus/dashboard de métricas. Cabeçalho + log bastam.

DEFINIÇÃO DE PRONTO
Distingo respostas cacheadas das recalculadas pelo cabeçalho e pelos logs.
```

---

# Fase 3 — Série histórica e cálculos

## História 8 — Acumular a série temporal de preços

```
HISTÓRIA
Como sistema, quero acumular cada preço coletado numa série temporal no Valkey, para ter
matéria-prima para os indicadores.

TAREFA
No caminho de MISS, além de cachear o resultado, grave o preço bruto numa série sob
"serie:bitcoin:precos". Use estrutura adequada (sorted set com timestamp como score, ou
list) e limite o tamanho (últimos N pontos, N em config.py). Documente no código a escolha.
Exponha em services/cache.py uma função que lê os últimos N preços em ordem cronológica.

CRITÉRIOS DE ACEITE
- Cada MISS adiciona um ponto (preço + timestamp).
- A série mantém no máximo N pontos.
- Função devolve os últimos N preços ordenados.

FORA DE ESCOPO
- Ainda não calcular indicadores. Só acumular e ler.

DEFINIÇÃO DE PRONTO
Após algumas coletas, leio do Valkey a série de preços recentes.
```

## História 9 — Média móvel

```
HISTÓRIA
Como usuário, quero ver a média móvel dos últimos N preços no painel, para acompanhar a
tendência sem o ruído de cada oscilação.

TAREFA
Crie backend/services/indicators.py com media_movel(precos: list[float]) -> float. Na rota
(MISS), leia a série (História 8), calcule e inclua o campo media_movel no JSON. Garanta que
o CardMoeda no Angular exibe o valor.

CRITÉRIOS DE ACEITE
- media_movel([100,102,101,103,104]) == 102.
- Sem pontos suficientes → campo null e o Angular mostra "—" sem quebrar.
- O cálculo mora só em indicators.py; a rota apenas orquestra.

FORA DE ESCOPO
- Sem volatilidade. Sem gráfico de linha (só o número).

DEFINIÇÃO DE PRONTO
O card exibe a média móvel, que estabiliza conforme a série cresce.
```

## História 10 — Volatilidade

```
HISTÓRIA
Como usuário, quero ver a volatilidade da moeda no painel, para saber o quanto o preço
oscila.

TAREFA
Em indicators.py, adicione volatilidade(precos: list[float]) -> float (desvio-padrão dos
preços ou dos retornos da janela). Integre na rota (MISS), preenchendo o campo volatilidade.
O CardMoeda exibe o valor.

CRITÉRIOS DE ACEITE
- Resultado correto para uma lista conhecida (valide manualmente).
- Poucos pontos → null, tratado no Angular sem erro.
- Documente: populacional ou amostral; sobre preços ou retornos.

FORA DE ESCOPO
- Sem indicadores extras (RSI, bandas). Só volatilidade.

DEFINIÇÃO DE PRONTO
O card mostra os quatro indicadores completos.
```

---

# Fase 4 — Amadurecimento da aplicação

## História 11 — Múltiplas moedas

```
HISTÓRIA
Como usuário, quero acompanhar várias moedas ao mesmo tempo, para ter um painel de verdade.

TAREFA
Generalize para uma lista de moedas em config.py (ex: bitcoin, ethereum, solana). Cada moeda
tem chave de cache e série próprias. GET /api/dashboard passa a devolver uma lista de objetos.
O Angular renderiza um CardMoeda por item (ex: *ngFor).

CRITÉRIOS DE ACEITE
- Adicionar moeda em config.py faz surgir um card novo, sem mudar código de rota.
- Cache e série independentes por moeda (chaves distintas).
- Falha ao buscar uma moeda não derruba as demais.

FORA DE ESCOPO
- Sem busca/filtro/ordenação na UI.

DEFINIÇÃO DE PRONTO
O painel mostra vários cards, cada um com seus indicadores, a partir da config.
```

## História 12 — Setup do Celery com Valkey como broker

```
HISTÓRIA
Como sistema, quero um worker Celery conectado ao Valkey e o caminho de coleta refatorado
como tarefa, para preparar o terreno do processamento assíncrono.

TAREFA
1) Refatore o caminho "coleta preço → atualiza série → calcula indicadores → grava cache"
   para uma função única em backend/services/pipeline.py (ex: processar_moeda(coin_id)). A
   rota do MISS passa a chamá-la, sem duplicar lógica.
2) Crie backend/celery_app.py com uma instância Celery usando o Valkey como broker E como
   result backend (URLs vindas de config.py / env).
3) Crie backend/tasks.py com uma task que chama pipeline.processar_moeda(coin_id).
4) No docker-compose.yml, adicione um serviço "worker" (mesma imagem do backend, comando
   `celery -A celery_app worker`), apontando broker/backend para o Valkey local.
5) Acrescente celery ao requirements.txt.

CRITÉRIOS DE ACEITE
- `docker compose up` sobe Valkey + backend + worker, e o worker conecta no broker.
- Disparar a task manualmente (ex: via shell) executa o pipeline e grava o resultado no Valkey.
- A rota do MISS e a task usam o MESMO pipeline.py (nenhuma lógica duplicada).

FORA DE ESCOPO
- Sem agendamento periódico ainda (é a próxima história — precisa do beat).

DEFINIÇÃO DE PRONTO
Chamo a task pelo Celery e vejo o resultado aparecer no Valkey, executado pelo worker.
```

## História 13 — Pré-cálculo agendado com Celery Beat (batch)

```
HISTÓRIA
Como sistema, quero uma tarefa periódica agendada pelo Celery Beat que pré-calcula os
indicadores de todas as moedas, para conhecer o processamento em batch além do sob demanda.

TAREFA
Configure o Celery Beat com um schedule que, a cada intervalo configurável (constante em
config.py), dispare a task para cada moeda (reusando a task da História 12). Adicione ao
docker-compose.yml um serviço "beat" (mesma imagem, comando `celery -A celery_app beat`).
Documente no README a diferença entre o caminho reativo (cache-aside sob demanda) e o
proativo (batch agendado). Respeite os limites da CoinGecko ao escolher o intervalo.

CRITÉRIOS DE ACEITE
- Com worker + beat rodando, os indicadores são atualizados sozinhos no intervalo definido.
- Após o beat rodar, /api/dashboard retorna majoritariamente HIT.
- Existe exatamente UMA fonte de agendamento (um único beat) — sem agendadores duplicados.
- O caminho sob demanda continua como fallback.

FORA DE ESCOPO
- Sem filas múltiplas, roteamento avançado ou retries sofisticados. Um schedule simples basta.

DEFINIÇÃO DE PRONTO
Com o beat ativo, o painel serve quase sempre do cache; o README explica os dois modelos.
```

---

# Fase 5 — Provisionamento na AWS com Terraform

> Ordem importa: rede → registro de imagem → cache → serviços → frontend → amarração.
> A partir daqui, `terraform destroy` ao fim de cada sessão.

## História 14 — Base do Terraform e rede (VPC)

```
HISTÓRIA
Como operador, quero a fundação do Terraform e a rede na AWS, para ter onde os demais
recursos vivem.

TAREFA
Em infra/, crie main.tf (provider aws com região via variável), variables.tf e outputs.tf.
Em network.tf, provisione uma VPC com subnets públicas e privadas em 2 AZs, internet gateway
e tabelas de rota. Para evitar custo de NAT Gateway neste projeto de estudo, planeje as
tasks Fargate em subnet pública com IP público (assign_public_ip) para alcançar CoinGecko e
ECR; o ElastiCache ficará em subnet privada. Documente esse trade-off em comentário.
Configure o state remoto (S3 + DynamoDB lock) OU deixe local e comente como migrar depois.

CRITÉRIOS DE ACEITE
- `terraform init` e `terraform plan` rodam sem erro.
- A VPC, subnets (públicas e privadas), IGW e rotas aparecem no plan.
- Região e CIDRs são variáveis, não valores fixos no meio do código.

FORA DE ESCOPO
- Nenhum ECS/ElastiCache/S3 ainda (próximas histórias).

DEFINIÇÃO DE PRONTO
`terraform apply` cria a rede; os IDs saem como outputs. Depois, `terraform destroy` limpa.
```

## História 15 — Repositório de imagem (ECR) + push do BFF

```
HISTÓRIA
Como operador, quero um repositório ECR e a imagem do backend publicada nele, para o Fargate
ter o que rodar (a MESMA imagem serve BFF, worker e beat).

TAREFA
Garanta um Dockerfile em backend/ (imagem enxuta que serve tanto o Uvicorn quanto o Celery,
variando só o comando de entrada). Em infra/ecr.tf, crie um repositório ECR. Documente os
comandos de build, login e push da imagem. Exponha a URL do repositório como output.

CRITÉRIOS DE ACEITE
- `terraform apply` cria o repositório ECR.
- Sigo os comandos documentados e a imagem sobe para o ECR.
- A URL do repositório sai como output.

FORA DE ESCOPO
- Sem automação de CI/CD ainda (História 20). Build/push manual aqui.

DEFINIÇÃO DE PRONTO
Vejo a imagem do backend listada no meu repositório ECR.
```

## História 16 — ElastiCache for Valkey

```
HISTÓRIA
Como operador, quero um Valkey gerenciado na AWS (ElastiCache), para servir de cache, série e
broker do Celery em produção sem eu administrar servidor.

TAREFA
Em infra/elasticache.tf, provisione ElastiCache for Valkey (engine = valkey) no tamanho mais
barato (ex: cache.t4g.micro, nó único), num subnet group nas subnets privadas, com um
security group próprio. Exponha o endpoint primário como output. NÃO abra o security group
para o mundo — a regra de entrada virá do security group das tasks (História 19).

CRITÉRIOS DE ACEITE
- `terraform apply` cria o cluster ElastiCache for Valkey.
- O endpoint sai como output.
- O security group do cache começa fechado (sem ingress público).

FORA DE ESCOPO
- Sem réplicas/cluster mode. Nó único basta para estudo.

DEFINIÇÃO DE PRONTO
Tenho o endpoint do ElastiCache for Valkey disponível como output do Terraform.
```

## História 17 — ECS Fargate: BFF (ALB) + worker + beat

```
HISTÓRIA
Como operador, quero o BFF, o worker Celery e o beat rodando em ECS Fargate, para servir a
API e processar tarefas de forma escalável e resiliente.

TAREFA
Em infra/ecs.tf, provisione um cluster ECS e TRÊS serviços a partir da mesma imagem do ECR,
variando o comando:
- Serviço BFF: task rodando Uvicorn, atrás de um ALB (target group + listener HTTP),
  security groups (ALB aceita 80 do mundo; task aceita a porta do container só do ALB),
  1–2 réplicas.
- Serviço worker: task rodando `celery worker`, sem ALB, 1+ réplicas.
- Serviço beat: task rodando `celery beat`, com EXATAMENTE 1 réplica (dois beats causariam
  agendamento duplicado — garanta desired_count = 1).
Todas as tasks recebem, via variável de ambiente, o endpoint do ElastiCache como host do
Valkey e como URL de broker/backend do Celery. Logs no CloudWatch. Exponha o DNS do ALB como
output.

CRITÉRIOS DE ACEITE
- `terraform apply` sobe cluster, os três serviços e o ALB.
- http://<dns-do-alb>/api/dashboard responde (BFF saudável).
- O serviço beat tem exatamente 1 réplica; worker e BFF podem escalar.
- Worker e beat conectam no mesmo Valkey (broker) que o BFF.

FORA DE ESCOPO
- Sem HTTPS/ACM/Route53. Sem auto scaling ainda.

DEFINIÇÃO DE PRONTO
A API responde pelo ALB e as tarefas periódicas rodam no worker, tudo em Fargate.
```

## História 18 — Frontend Angular em S3 + CloudFront

```
HISTÓRIA
Como operador, quero o Angular publicado em S3 e distribuído via CloudFront, para servir o
frontend estático globalmente e barato.

TAREFA
Em infra/frontend.tf, crie um bucket S3 privado para o build do Angular e uma distribuição
CloudFront com Origin Access Control lendo desse bucket, com fallback de rota para
index.html (SPA). Documente: `ng build` gera o dist/, sincronizado para o S3; depois uma
invalidação do CloudFront. Exponha a URL do CloudFront como output.

CRITÉRIOS DE ACEITE
- `terraform apply` cria bucket + distribuição CloudFront.
- Sigo os comandos, subo o build e a URL do CloudFront serve a app Angular.
- O bucket não é público; o acesso é só via CloudFront (OAC).

FORA DE ESCOPO
- Sem domínio custom/HTTPS próprio (usar o domínio padrão do CloudFront).

DEFINIÇÃO DE PRONTO
Abro a URL do CloudFront e vejo o dashboard Angular carregando.
```

## História 19 — Amarração: rede, segredos e URL da API

```
HISTÓRIA
Como operador, quero ligar as peças com segurança e configuração corretas, para o sistema
funcionar fim a fim na AWS.

TAREFA
1) Adicione a regra de ingress no security group do ElastiCache aceitando a porta do Valkey
   APENAS a partir do security group das tasks Fargate (vale para BFF, worker e beat).
2) Garanta que todas as tasks recebem o endpoint do Valkey por env var (e segredos, se
   houver, via SSM Parameter Store / Secrets Manager — não em texto plano).
3) Aponte a environment de produção do Angular para o DNS do ALB e reconstrua/publique.
4) Ajuste CORS no BFF para aceitar a origem do CloudFront.
Revise os outputs: DNS do ALB, URL do CloudFront, endpoint do Valkey.

CRITÉRIOS DE ACEITE
- BFF, worker e beat conectam no ElastiCache (dashboard mostra HIT/MISS reais; o beat atualiza
  sozinho em produção).
- O Angular no CloudFront chama o BFF no ALB sem erro de CORS.
- Nenhum segredo em texto plano no código ou no state.

FORA DE ESCOPO
- Sem WAF, sem HTTPS custom, sem observabilidade avançada.

DEFINIÇÃO DE PRONTO
Fluxo completo na AWS: CloudFront (Angular) → ALB (BFF/Fargate) → ElastiCache (Valkey),
com worker/beat atualizando os dados em background.
```

---

# Fase 6 — Deploy contínuo (opcional)

## História 20 — Pipeline CI/CD

```
HISTÓRIA
Como desenvolvedor, quero que um push no repositório publique frontend e backend
automaticamente, para parar de fazer deploy na mão.

TAREFA
Crie um workflow (ex: GitHub Actions) com dois fluxos:
- Backend: build da imagem, push no ECR e atualização dos serviços ECS que usam essa imagem
  — BFF, worker E beat (novo deployment em cada um).
- Frontend: `ng build`, sync do dist/ para o S3 e invalidação do CloudFront.
Use credenciais AWS via segredos do repositório (idealmente OIDC, sem chave estática).
Documente os segredos necessários.

CRITÉRIOS DE ACEITE
- Um push na branch principal dispara o pipeline.
- BFF, worker e beat são reimplantados no ECS com a nova imagem (rolling update).
- O frontend novo aparece na URL do CloudFront após a invalidação.

FORA DE ESCOPO
- Sem ambientes múltiplos (staging/prod) nem aprovações manuais. Um ambiente basta.

DEFINIÇÃO DE PRONTO
Um push publica frontend e backend (incluindo worker e beat) sozinho.
```

---

## Como conduzir cada bolt (ciclo AI-DLC)

1. Cole o **Prompt Base** (ou tenha-o como arquivo de regras do projeto).
2. Cole **uma** história.
3. Leia o plano que o agente propõe e aprove ou ajuste **antes** de deixar codar.
4. Rode o "Definição de pronto" manualmente. Só avance quando passar.
5. Faça commit ao fim de cada história — cada uma vira um ponto de restauração.
6. Nas histórias de infra (Fase 5+), rode `terraform destroy` ao encerrar a sessão para não
   acumular custo.
