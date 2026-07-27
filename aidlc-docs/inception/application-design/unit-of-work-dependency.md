# Dependências entre unidades — revisão

```text
U1 (esqueleto)
  -> U2 (cache)
       -> U3 (série/indicadores)
            -> U4 (multi + Celery)
                 -> U5 (AWS)
                      -> U6 (CI/CD, opcional)
```

| Unidade | Depende de | Contrato crítico |
|---|---|---|
| U1 | — | `/api/dashboard` + CardMoeda |
| U2 | U1 | mesmas chaves/contrato + Valkey |
| U3 | U2 | série no MISS + campos MM/vol |
| U4 | U3 | pipeline único + multi-moedas |
| U5 | U4 | imagem Docker + app estável |
| U6 | U5 | ECR/ECS/S3/CF existentes |
