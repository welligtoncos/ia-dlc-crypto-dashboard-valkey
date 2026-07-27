# Componentes — market-dashboard

## Camada BFF (Python / FastAPI)

### MarketDataSource
- **Propósito**: Isolar a fonte externa CoinGecko
- **Responsabilidades**: Buscar preço e série histórica; tratar timeout/erro HTTP/formato; não calcular indicadores; não acessar Valkey
- **Arquivo alvo**: `backend/services/coingecko.py`

### CacheStore
- **Propósito**: Wrapper Valkey (redis-py)
- **Responsabilidades**: get/set/delete com TTL; chaves por moeda/endpoint; sem regra de negócio nem cálculo
- **Arquivo alvo**: `backend/services/cache.py`

### IndicatorsEngine
- **Propósito**: Cálculos puros de indicadores
- **Responsabilidades**: variação % 24h, SMA(7), volatilidade (janela 7); parâmetros via config; sem I/O de rede/cache
- **Arquivo alvo**: `backend/services/indicators.py`

### MarketIndicatorsService
- **Propósito**: Application Service — orquestra cache → fonte → indicadores
- **Responsabilidades**: decidir hit/miss/stale; montar payload agregado; definir flag `degraded`; mapear falhas para erros de aplicação
- **Arquivo alvo**: `backend/services/market_indicators.py` *(adição ao scaffold original, aprovada no design)*

### ApiRoutes
- **Propósito**: Camada HTTP fina
- **Responsabilidades**: expor `GET /api/indicators`; converter erros em 502/503; sem orquestração de negócio
- **Arquivo alvo**: `backend/main.py`

### AppConfig
- **Propósito**: Configuração
- **Responsabilidades**: moedas, TTLs, URLs, host Valkey via env
- **Arquivo alvo**: `backend/config.py`

---

## Camada Frontend (Angular)

### MarketApiService
- **Propósito**: Cliente HTTP do BFF
- **Responsabilidades**: chamar `GET /api/indicators` via HttpClient + URL de environment; sem cálculos
- **Arquivo alvo**: `frontend/src/app/...` (serviço)

### DashboardComponent
- **Propósito**: UI única do painel
- **Responsabilidades**: tabela (moeda, preço, var%, SMA, volatilidade), botão atualizar, banner global de degradação + marca por linha
- **Arquivo alvo**: componente standalone Angular

---

## Camada Deploy lógico (AWS)

### Network
- VPC/subnets base para os demais recursos

### CacheManaged
- ElastiCache for Valkey consumido pelo BFF

### BffRuntime
- ECR + ECS Fargate + ALB servindo o BFF

### FrontendCdn
- S3 + CloudFront servindo o build Angular

### LocalStackRuntime (Compose)
- Não é AWS; sobe Valkey + backend + frontend para estudo local
