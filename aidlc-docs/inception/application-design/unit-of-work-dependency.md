# Dependências entre Unidades

## Matriz

| Unidade | Depende de | Bloqueia |
|---|---|---|
| U1 BFF | — | U2, U3 |
| U2 Frontend | U1 (contrato `GET /api/indicators` estável) | U3 (para publicar FE real) |
| U3 Infra | U1 (imagem/Dockerfile BFF), U2 (build Angular) | — |

## Grafo

```text
U1 (BFF + Compose)
        |
        v
U2 (Frontend Angular)
        |
        v
U3 (Terraform AWS)
        |
        v
Build e Testes
```

## Contratos de integração

| De → Para | Contrato |
|---|---|
| U2 → U1 | HTTP `GET /api/indicators` (JSON com indicadores + `degraded`) |
| U3 → U1 | Imagem Docker do backend + env (Valkey ElastiCache, etc.) |
| U3 → U2 | Artefatos estáticos do build Angular + env de produção (URL ALB) |
| Compose (U1) → U2 | Serviço frontend no Compose; pode iniciar como placeholder e ser substituído na U2 |

## Regras
- Não iniciar U2 antes do contrato da API definido/implementado na U1
- Não aplicar Terraform (U3) antes de haver artefatos U1/U2 para publicar
- Em U3: sempre revisar `terraform plan` antes de sugerir `apply`
