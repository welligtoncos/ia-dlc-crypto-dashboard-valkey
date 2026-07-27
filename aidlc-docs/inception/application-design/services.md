# Serviços e orquestração — revisão

## Caminho reativo (cache-aside)
1. Rota lê cache (`dashboard:{coin}:indicadores`)
2. HIT → retorna + `X-Cache: HIT`
3. MISS → `pipeline.processar_moeda` → grava cache/série → `X-Cache: MISS`
4. CoinGecko falha → 502 (ou degradação parcial multi-moeda na H11)

## Caminho proativo (H13)
- Beat agenda tasks → worker executa `pipeline.processar_moeda` → cache quente → rota majoritariamente HIT

## Regra de ouro
**Uma** implementação do caminho coleta→série→cálculo→cache: `pipeline.py`.  
Rota MISS e task Celery apenas chamam.

## Frontend
Só consome BFF; sem CoinGecko; sem cálculos.
