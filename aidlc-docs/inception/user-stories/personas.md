# Personas — market-dashboard

## P1 — Visitante do Painel

| Atributo | Descrição |
|---|---|
| **Nome** | Visitante do Painel |
| **Tipo** | Usuário anônimo (painel público de estudo) |
| **Objetivo** | Consultar rapidamente preço, variação %, SMA e volatilidade de BTC, ETH e SOL |
| **Motivações** | Entender o mercado cripto sem instalar ferramentas; ver dados atualizados sob demanda |
| **Comportamento** | Abre o painel, lê a tabela de indicadores e usa o botão atualizar quando quiser dados frescos |
| **Dores** | Dados demorando, tela vazia sem feedback, números inconsistentes ou sem contexto de falha da fonte |
| **Expectativas** | Interface simples; indicadores já calculados; se a fonte externa falhar, ainda ver último dado disponível com aviso de degradação |
| **Não é** | Administrador, trader autenticado ou operador de infra — não há login |

### Relação com o sistema
- Consome apenas o **frontend Angular**.
- Beneficia-se indiretamente do BFF, Valkey, Compose e da infra AWS (histórias técnicas escritas com o Visitante como beneficiário).
