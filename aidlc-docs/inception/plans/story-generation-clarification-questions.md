# Esclarecimento — Plano de Histórias

Detectei uma ambiguidade nas respostas do plano:

- **Pergunta 1 = B**: apenas a persona **Visitante do Painel**
- **Pergunta 4 = A**: formato “Como [persona], quero…, para…”
- Porém há histórias técnicas (Compose, BFF, Terraform) cujo ator direto não é o visitante

---

## Pergunta de Esclarecimento 1
Como escrever as histórias técnicas (Compose, BFF, Infra) tendo só a persona Visitante?

A) Usar o Visitante como beneficiário nas histórias técnicas (ex.: “Como Visitante, quero que os indicadores estejam disponíveis via BFF…”) — enablers escritos pelo valor ao usuário final

B) Manter só Visitante em `personas.md`, mas permitir formato compacto (título + critérios) nas histórias técnicas; formato “Como…” só nas histórias de UI

C) Incluir também a persona Desenvolvedor/Estudante (voltar à opção A da Pergunta 1) e usá-la nas histórias técnicas

D) Outro (descreva após a tag [Answer]: abaixo)

[Answer]: A
