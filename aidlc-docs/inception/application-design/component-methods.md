# Métodos (alto nível) — revisão

## CoinGeckoClient
```python
def get_market_data(coin_id: str) -> dict  # {preco, variacao_24h}
```

## CacheStore
```python
def get(chave: str) -> dict | None
def set(chave: str, valor: dict, ttl: int) -> None
def ping() -> bool
def append_preco(serie_key: str, preco: float, ts: float, max_n: int) -> None
def get_ultimos_precos(serie_key: str, n: int) -> list[float]
```

## IndicatorsEngine
```python
def media_movel(precos: list[float]) -> float | None
def volatilidade(precos: list[float]) -> float | None  # documentar fórmula na H10
```

## Pipeline
```python
def processar_moeda(coin_id: str) -> dict  # contrato dashboard de uma moeda
```

## ApiRoutes
```python
@app.get("/api/dashboard")
def dashboard(refresh: bool = False) -> list[dict] | dict  # dict até H10; list a partir H11
```

## Celery
```python
@app.task
def processar_moeda_task(coin_id: str) -> dict
# beat: schedule periódico por moeda da config
```

## Frontend
```typescript
// DashboardService
getDashboard(): Observable<DashboardItem | DashboardItem[]>
// CardMoeda @Input() dados
```
