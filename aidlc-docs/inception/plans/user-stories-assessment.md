# Avaliação — Histórias de Usuário

## Análise do Pedido
- **Pedido original**: Dashboard de mercado cripto com BFF, Angular e Terraform AWS, construído em etapas
- **Impacto no usuário**: Direto (painel web público com indicadores)
- **Nível de complexidade**: Moderada–Alta (múltiplas camadas + lógica de indicadores + cache + infra)
- **Stakeholders**: Estudante/dev do projeto; consumidor do painel (usuário anônimo)

## Critérios Atendidos
- [x] Alta prioridade: novas funcionalidades voltadas ao usuário
- [x] Alta prioridade: API/serviço consumido pelo frontend (BFF customer-facing interno)
- [x] Alta prioridade: lógica de negócio com múltiplos cenários (cache hit/miss, degradação CoinGecko)
- [x] Benefícios: critérios de aceite testáveis por história; alinhamento com RF-07 (BFF → FE → Infra)

## Decisão
**Executar Histórias de Usuário**: Sim

**Justificativa**: Projeto greenfield com UI, BFF e regras de degradação. Histórias com critérios de aceite reduzem ambiguidade na construção etapa a etapa e suportam PBT nos indicadores.

## Resultados Esperados
- Personas claras (visitante do painel + desenvolvedor/estudante)
- Histórias INVEST alinhadas às 3 unidades de construção
- Critérios de aceite verificáveis manualmente e por testes
