# Plano de Execução — revisão (fonte 20 histórias)

## Análise
- **Risco:** Médio–Alto (Celery + AWS com custo)
- **Impacto:** FE, BFF, cache, série, assíncrono, IaC, CI/CD opcional
- **Fonte:** `prompts-fonte-normativa.md`

## Estágios Inception (esta revisão)
- [x] Workspace Detection (já greenfield)
- [x] Reverse Engineering SKIP
- [x] Requirements (reescrito da fonte)
- [x] User Stories (20 histórias)
- [x] Workflow Planning (este doc)
- [x] Application Design (pipeline/Celery/cards)
- [x] Units Generation (U1–U6 por fase)

## Construction (por unidade/fase)
| Unidade | FD | NFR | NFR Design | Infra Design | Code Gen |
|---|---|---|---|---|---|
| U1 H01–04 | mínimo | mínimo | skip/mín | SKIP | EXECUTE por história |
| U2 H05–07 | leve | TTL/obs | leve | SKIP | EXECUTE |
| U3 H08–10 | EXECUTE + PBT | EXECUTE | EXECUTE | SKIP | EXECUTE |
| U4 H11–13 | EXECUTE | Celery/broker | EXECUTE | SKIP | EXECUTE |
| U5 H14–19 | SKIP | custo/sizing | leve | EXECUTE | EXECUTE + plan/destroy |
| U6 H20 | SKIP | CI secrets | leve | leve | EXECUTE |

Build e Testes: após U4 (local) e após U5 (AWS smoke).

## Visualização (texto)
```text
INCEPTION (revisado) COMPLETE -> aguardando aprovacao
CONSTRUCTION: H01..H20 uma por vez
  U1 -> U2 -> U3 -> U4 -> U5 -> [U6]
```

## Regras
- Plano curto + OK antes de cada história
- Não antecipar escopo da próxima
- AWS: plan → apply → destroy ao fim da sessão
