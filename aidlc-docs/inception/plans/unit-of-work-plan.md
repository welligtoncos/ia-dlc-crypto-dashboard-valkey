# Plano de Geração de Unidades de Trabalho — market-dashboard

**Status**: Parte 2 — Geração concluída (aguardando aprovação das unidades)  
**Base**: requirements, stories, application-design, execution-plan  
**Idioma**: Português

### Decisões consolidadas
| Tema | Decisão |
|---|---|
| Unidades | U1 BFF+Compose, U2 Frontend, U3 Infra |
| Mapa de histórias | E1→U1, E2→U2, E3→U3 |
| Sequência | Estrita: U1 → U2 → U3 |
| Código | Monorepo `market-dashboard/{backend,frontend,infra}` + compose |
| Deploy | BFF container / FE estático / IaC AWS; local via Compose |
| Compose na U1 | Valkey+backend+frontend (FE pode ser placeholder até U2) |
| Granularidade | Histórias pequenas como checklist interno de cada unidade |

## Instruções
Preencha cada `[Answer]:`. Após respostas + aprovação deste plano, serão gerados:
- `unit-of-work.md`
- `unit-of-work-dependency.md`
- `unit-of-work-story-map.md`

---

## Contexto já alinhado
- RF-07 / histórias: BFF → Frontend → Infra
- Design: MarketIndicatorsService orquestra; FE só HTTP; infra lógica AWS
- Compose: Valkey + backend + frontend na U1 (história US-BFF-01)

---

## Perguntas de Decomposição

## Pergunta 1 — Número e fronteiras das unidades
Como decompor o sistema?

A) 3 unidades: U1 BFF+Compose/Valkey/indicadores, U2 Frontend Angular, U3 Infra Terraform (como RF-07)

B) 4 unidades: U0 Scaffold/Compose, U1 BFF, U2 Frontend, U3 Infra

C) 2 unidades: U1 App completa local (BFF+FE+Compose), U2 Infra AWS

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 2 — Agrupamento das histórias
Como mapear histórias → unidades?

A) Por épico já definido: E1→U1, E2→U2, E3→U3 (US-BFF-* / US-FE-* / US-INF-*)

B) Reagrupar: Compose sozinho em unidade inicial; restante igual a A

C) Agrupar por deployável (BFF service, FE static, IaC) ignorando a ordem das histórias no arquivo

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 3 — Dependências entre unidades
Qual regra de sequência na construção?

A) Estrita: U1 completa antes de U2; U2 antes de U3 (sem paralelismo)

B) U1 obrigatória primeiro; U2 e U3 podem planejar em paralelo após contrato da API estabilizado em U1

C) Livre — ordem definida história a história no chat, sem dependência formal no mapa

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 4 — Organização de código (greenfield)
Onde fica o código das unidades no repo?

A) Monorepo `market-dashboard/` com pastas `backend/`, `frontend/`, `infra/` + `docker-compose.yml` na raiz do app (estrutura já definida)

B) Três roots separados no workspace (sem pasta `market-dashboard/` agregadora)

C) Backend e frontend sob `market-dashboard/`; infra em pasta `infra/` na raiz do workspace

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 5 — Modelo de deploy por unidade
Como tratar deployabilidade?

A) U1 = serviço BFF (container); U2 = artefato estático Angular; U3 = IaC que publica U1/U2 na AWS; local via Compose

B) Tudo como um único deployável local; AWS só no fim sem distinguir artefatos

C) Cada história US-INF-* é um “mini-deploy” independente sem unidade Infra única

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 6 — Escopo da U1 além do BFF
O `docker-compose` sobe também o frontend. O que entra formalmente na U1?

A) U1 inclui Compose completo (Valkey+backend+frontend), mesmo que a UI final seja U2 — frontend no Compose pode ser placeholder/espelho até U2

B) U1 Compose sobe só Valkey+backend; frontend no Compose é adicionado na U2 (ajuste pontual do compose)

C) U1 só código BFF; Compose fica como critério compartilhado documentado, implementado quando necessário

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 7 — Granularidade interna das unidades
Nas unidades, o trabalho interno deve:

A) Seguir as histórias pequenas já escritas (US-BFF-01…06 etc.) como checklist de implementação dentro da unidade

B) Tratar cada unidade como um único pacote sem subdividir por histórias na construção

C) Subdividir só U1 por módulos (cache / indicadores / API); U2 e U3 como bloco único cada

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

---

## Checklist de geração (após aprovação)

- [x] Gerar `unit-of-work.md` com definições, responsabilidades e organização de código
- [x] Gerar `unit-of-work-dependency.md` com matriz de dependências
- [x] Gerar `unit-of-work-story-map.md` mapeando todas as histórias
- [x] Validar fronteiras e cobertura de histórias
- [x] Atualizar `aidlc-state.md` e `audit.md`
- [x] Apresentar unidades para aprovação (gate para Construction)

## Artefatos obrigatórios
- [x] `unit-of-work.md`
- [x] `unit-of-work-dependency.md`
- [x] `unit-of-work-story-map.md`
