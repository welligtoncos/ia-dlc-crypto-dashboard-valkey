# Market Dashboard (local)

Stack: Angular + FastAPI (BFF) + Valkey + Celery (worker + beat).

## Subir o ambiente

```bash
docker compose up -d --build
```

Sobe: `valkey`, `backend` (:8000), `worker`, `beat`.

Frontend (em outro terminal):

```bash
cd frontend
npm start
```

## Dois modelos de atualização

### Reativo (cache-aside sob demanda)

1. O Angular chama `GET /api/dashboard`.
2. Se a chave `dashboard:{moeda}:indicadores` existir no Valkey → **HIT** (sem CoinGecko).
3. Se não existir (ou `?refresh=true`) → **MISS**: a rota chama `pipeline.processar_moeda` (coleta → série → indicadores → cache).

Esse caminho continua como **fallback** quando o cache está frio ou o usuário força refresh.

### Proativo (batch agendado — Celery Beat)

1. O serviço **beat** (um único processo) agenda, a cada `BEAT_INTERVAL_SECONDS` (default 60), a task `processar_moeda_task` para cada moeda em `DASHBOARD_COIN_IDS`.
2. O **worker** executa a mesma `pipeline.processar_moeda` da rota.
3. O cache fica quente → `/api/dashboard` tende a ser **HIT**.

Não suba mais de um container `beat`: dois beats duplicariam o agendamento.

## Rate limit CoinGecko

API pública keyless ≈ 10–50 req/min. Com 3 moedas e intervalo 60s ≈ 3 req/min.  
Ajuste via env: `BEAT_INTERVAL_SECONDS`, `CACHE_TTL_SECONDS`, `DASHBOARD_COIN_IDS`.

## Checagens rápidas

```bash
curl -i http://localhost:8000/api/dashboard   # ver header X-Cache
docker compose logs beat --tail 30
docker compose logs worker --tail 30
```
