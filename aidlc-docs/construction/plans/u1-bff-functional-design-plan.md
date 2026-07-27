# Plano de Design Funcional — U1 BFF

**Unidade**: U1 — BFF + Compose + indicadores  
**Status**: Planejamento (aguardando respostas)  
**Idioma**: Português  
**PBT**: Habilitado — identificar propriedades testáveis nos indicadores

## Instruções
Preencha cada `[Answer]:`. Após respostas + aprovação, serão gerados:
- `business-logic-model.md`
- `business-rules.md`
- `domain-entities.md`
- (sem `frontend-components.md` — UI é U2)

---

## Perguntas

## Pergunta 1 — Modelo do payload de indicadores
Como estruturar a resposta de `GET /api/indicators`?

A) Objeto com `degraded: bool` global + `items: [{ coin_id, symbol, price, change_24h_pct, sma, volatility, degraded? }]`

B) Lista pura de itens; cada item com `degraded`; sem flag global (UI deriva o banner se algum item degradado)

C) Objeto com `generated_at`, `degraded`, `items` como em A, mais `source: "live" | "cache" | "stale"`

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 2 — O que é cacheado no Valkey
Qual granularidade de cache na lógica de negócio?

A) Cache do payload final por moeda (`indicators:{coin_id}`) com TTL de preços; histórico separado (`history:{coin_id}`) com TTL maior

B) Apenas payload final agregado de todas as moedas (`indicators:all`) com um TTL

C) Apenas séries brutas da CoinGecko; indicadores sempre recalculados a partir do histórico em cache

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 3 — Definição de SMA e volatilidade
Como fechar as regras de cálculo (janela 7)?

A) SMA = média aritmética dos últimos 7 **preços de fechamento diários**; volatilidade = desvio-padrão amostral dos retornos log/simples diários × 100 (percentual), janela 7; variação 24h = (now - price_24h)/price_24h × 100

B) Igual a A, mas volatilidade = desvio-padrão dos **preços** (não dos retornos)

C) Usar campo `price_change_percentage_24h` da CoinGecko para variação; SMA/volatilidade só sobre histórico diário como em A

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 4 — Série insuficiente
Se houver menos de 7 pontos para SMA/volatilidade?

A) Retornar esses indicadores como `null` e manter preço/variação se disponíveis; não marcar degraded só por isso

B) Falhar a moeda inteira (erro) se a janela não fechar

C) Usar janela parcial (média dos N disponíveis se N≥2) e flag `partial_window: true` no item

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 5 — Política stale / degraded
Quando marcar `degraded`?

A) Somente quando a CoinGecko falhou/timeout/formato inválido e a resposta veio de cache expirado (stale)

B) Sempre que a resposta vier de cache (mesmo dentro do TTL)

C) Em stale (como A) **ou** quando qualquer indicador da moeda for `null` por dados insuficientes

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 6 — Erro total vs parcial
Se a CoinGecko falhar para 1 moeda mas as outras ok?

A) Resposta 200 com as moedas ok; a moeda com falha usa stale se existir, senão item com erro/`null` e degraded; só 502/503 se **nenhuma** moeda puder ser montada

B) Qualquer falha parcial vira 502/503 da API inteira

C) Omitir a moeda com falha da lista (sem erro HTTP) se não houver stale

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 7 — Identificadores CoinGecko
Quais `coin_id` oficiais usar?

A) `bitcoin`, `ethereum`, `solana` (vs_currency `usd`)

B) Símbolos BTC/ETH/SOL mapeados via tabela em config (ids configuráveis)

C) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

## Pergunta 8 — Propriedades PBT prioritárias (indicadores)
Quais propriedades devem ser documentadas como obrigatórias no design funcional?

A) Invariantes: SMA entre min/max da janela; volatilidade ≥ 0; variação 0 se preços iguais; monotonicidade básica da média

B) Além de A: propriedade oracle com implementação de referência simples para SMA e desvio-padrão

C) Apenas testes example-based no design; PBT só na Code Gen sem listar propriedades agora

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: 

---

## Checklist de geração (após aprovação)

- [ ] Gerar `business-logic-model.md`
- [ ] Gerar `business-rules.md`
- [ ] Gerar `domain-entities.md` (incl. seção Testable Properties / PBT)
- [ ] Validar alinhamento com US-BFF-* e application-design
- [ ] Atualizar state/audit
- [ ] Apresentar para aprovação (próximo: NFR Requisitos U1)
