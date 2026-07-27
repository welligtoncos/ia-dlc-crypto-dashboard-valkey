# Métodos dos Componentes (alto nível)

> Regras de cálculo detalhadas ficam para o Design Funcional (U1). Aqui: assinaturas tipadas.

## MarketDataSource (`coingecko.py`)

```python
async def fetch_simple_price(coin_ids: list[str], vs_currency: str) -> dict[str, float]: ...
async def fetch_market_chart(coin_id: str, vs_currency: str, days: int) -> list[tuple[int, float]]: ...
```

- Retornos estruturados; erros de rede/formato → exceções tipadas do domínio de integração.

## CacheStore (`cache.py`)

```python
def get(key: str) -> bytes | None: ...
def set(key: str, value: bytes, ttl_seconds: int) -> None: ...
def delete(key: str) -> None: ...
```

## IndicatorsEngine (`indicators.py`)

```python
def percent_change_24h(price_now: float, price_24h_ago: float) -> float: ...
def sma(prices: list[float], window: int) -> float: ...
def volatility_pct(prices: list[float], window: int) -> float: ...
```

## MarketIndicatorsService (`market_indicators.py`)

```python
async def get_indicators() -> IndicatorsResponse: ...
```

- Orquestra CacheStore + MarketDataSource + IndicatorsEngine.
- `IndicatorsResponse` inclui lista por moeda e sinais de degradação.

## ApiRoutes (`main.py`)

```python
@app.get("/api/indicators")
async def get_indicators() -> IndicatorsResponse: ...
```

- Delega a `MarketIndicatorsService`; mapeia falhas sem cache → HTTP 502/503.

## AppConfig (`config.py`)

```python
# propriedades tipadas / settings
COINS: list[str]
PRICE_TTL_SECONDS: int
HISTORY_TTL_SECONDS: int
SMA_WINDOW: int
VOLATILITY_WINDOW: int
COINGECKO_BASE_URL: str
VALKEY_HOST: str
VALKEY_PORT: int
```

## MarketApiService (Angular)

```typescript
getIndicators(): Observable<IndicatorsResponse>;
```

## DashboardComponent (Angular)

```typescript
ngOnInit(): void;
refresh(): void; // botão atualizar
```

- Exibe banner se `degraded` global; badge/ícone por linha se o item estiver degradado.
