# Plano de Geração de Histórias de Usuário

**Projeto**: market-dashboard  
**Idioma**: Português  
**Base**: `aidlc-docs/inception/requirements/requirements.md`  
**Status**: Parte 2 — Geração concluída (aguardando aprovação das histórias)

### Decisões consolidadas
| Tema | Decisão |
|---|---|
| Personas | Apenas Visitante do Painel |
| Quebra | Híbrido: 3 épicos (BFF, Frontend, Infra) + histórias pequenas por capacidade |
| Formato | “Como [persona], quero…, para…” + critérios Given/When/Then |
| Histórias técnicas | Visitante como **beneficiário** (enablers pelo valor ao usuário final) |
| Compose | História própria no épico BFF/local |
| Infra | Uma história por grupo: rede, ElastiCache, ECS/ALB, S3/CloudFront |
| Ordem | RF-07: BFF (+ local) → Frontend → Infra |

---

## Instruções
Preencha cada `[Answer]:` com a letra da opção. Se escolher a última opção (**Outro**), descreva após a tag.  
Só após **todas** as respostas e aprovação deste plano é que as histórias serão geradas (`stories.md` e `personas.md`).

---

## Abordagens de Quebra (referência)

| Abordagem | Benefício | Trade-off |
|---|---|---|
| Jornada do usuário | Foco no fluxo de uso do painel | Pode misturar BFF e UI na mesma história |
| Por funcionalidade | Alinha bem a RF-01…RF-08 | Menos narrativa de persona |
| Por persona | Bom se houver vários papéis | Aqui há poucos papéis (painel público) |
| Por domínio | Separa mercado / cache / infra | Pode ficar técnico demais cedo |
| Por épico | Hierarquia épico → histórias | Extra overhead se o escopo já é pequeno |
| Híbrido (épicos por camada + histórias por capacidade) | Casa com RF-07 (BFF → FE → Infra) | Precisa regras claras de corte |

---

## Perguntas de Planejamento

## Pergunta 1 — Personas
Quais personas devemos documentar?

A) Duas: Visitante do Painel (usuário anônimo) e Desenvolvedor/Estudante (quem sobe e valida a stack)

B) Apenas Visitante do Painel

C) Três: Visitante, Desenvolvedor/Estudante e Operador de Infra (foco Terraform/AWS)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: B

## Pergunta 2 — Abordagem de quebra das histórias
Como organizar as histórias?

A) Híbrido: 3 épicos (BFF, Frontend, Infra) com histórias por capacidade dentro de cada épico — alinhado a RF-07

B) Por funcionalidade (sem épicos explícitos), ordenadas na sequência BFF → Frontend → Infra

C) Por jornada do usuário (do “abrir o painel” ao “ver indicadores atualizados”), com histórias técnicas como suporte

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 3 — Granularidade
Qual tamanho preferido das histórias?

A) Histórias pequenas e implementáveis isoladamente (ex.: cache separado de indicadores; tabela UI separada do serviço HttpClient)

B) Histórias médias por capacidade (ex.: “BFF de indicadores com cache e degradação” como uma história)

C) Uma história por unidade/épico (3 histórias grandes)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 4 — Formato das histórias
Qual formato usar em `stories.md`?

A) Padrão: “Como [persona], quero [objetivo], para [benefício]” + critérios de aceite em checklist

B) Formato compacto: título + descrição curta + critérios de aceite (sem frase “Como…”)

C) Formato A + rastreabilidade explícita para RF/RNF (ex.: “Cobre: RF-01, RF-03”)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 5 — Critérios de aceite
Qual nível de detalhe nos critérios de aceite?

A) Given/When/Then (ou equivalente) com cenários felizes e de erro (ex.: CoinGecko fora)

B) Checklist objetivo verificável manualmente (sem Gherkin formal)

C) Mistura: Gherkin só para fluxos críticos (indicadores + degradação); checklist para o restante

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 6 — Escopo das histórias de infra
As histórias de Terraform devem incluir o quê?

A) Uma história por grupo lógico: rede, cache ElastiCache, ECS/ALB, frontend S3/CloudFront (ainda no épico Infra)

B) Uma única história “Provisionar stack AWS de estudo” com critérios cobrindo todos os recursos

C) Duas histórias: backend na AWS (VPC/ECR/ECS/ALB/Valkey) e frontend estático (S3/CloudFront)

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 7 — História de ambiente local (Compose)
Como tratar o `docker-compose` (Valkey + backend + frontend)?

A) História própria no épico BFF/local (“Subir stack local containerizada”)

B) Critério de aceite embutido nas histórias de BFF e Frontend (sem história dedicada)

C) História no início, antes do BFF, como pré-requisito de desenvolvimento

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

## Pergunta 8 — Prioridade / ordem de geração
A ordem das histórias no arquivo deve seguir:

A) Exatamente RF-07: BFF (+ local) → Frontend → Infra

B) Ordem de valor para o visitante primeiro (UI primeiro), depois BFF e infra

C) Ordem técnica de dependência (Compose/Valkey → BFF → Frontend → Infra), mesmo que Compose seja história separada

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A

---

## Checklist de Execução (Parte 2 — após aprovação deste plano)

> Não marcar até a Parte 2. Checkboxes abaixo são o plano de geração.

- [x] Carregar este plano aprovado e as respostas das perguntas
- [x] Gerar `aidlc-docs/inception/user-stories/personas.md` conforme Pergunta 1
- [x] Gerar `aidlc-docs/inception/user-stories/stories.md` com histórias INVEST
- [x] Incluir critérios de aceite em cada história (conforme Perguntas 4 e 5)
- [x] Mapear personas ↔ histórias
- [x] Incluir rastreabilidade RF/RNF se a Pergunta 4 exigir (P4=A — rastreabilidade opcional; tabela de referência incluída ao final)
- [x] Organizar por abordagem da Pergunta 2 e ordem da Pergunta 8
- [x] Cobrir: indicadores BFF, cache Valkey, degradação CoinGecko, UI tabela+atualizar, Compose, Terraform AWS
- [x] Garantir que nenhuma história antecipe escopo fora dos requisitos
- [x] Atualizar `aidlc-state.md` e `audit.md`
- [x] Apresentar histórias geradas para aprovação explícita

---

## Artefatos Obrigatórios
- [x] `personas.md`
- [x] `stories.md` (INVEST + critérios de aceite + mapeamento persona)
