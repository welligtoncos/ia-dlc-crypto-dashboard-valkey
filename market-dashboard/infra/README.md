# Infra AWS (Terraform)

Ordem das histórias: rede (H14) → ECR (H15) → ElastiCache → ECS → frontend → amarração.

**Sempre:** `terraform plan` antes de `apply`. Ao fim da sessão de estudo: `terraform destroy`.

## Pré-requisitos

- Terraform >= 1.5
- AWS CLI configurada (`aws configure` / perfil)
- Docker (para build/push da imagem)

## H14 — Rede

```powershell
cd market-dashboard\infra
terraform init
terraform plan
terraform apply
```

## H15 — ECR + push da imagem do backend

A **mesma** imagem serve BFF, worker e beat (só muda o comando de entrada).

### 1) Criar o repositório

```powershell
cd market-dashboard\infra
terraform plan
terraform apply
terraform output ecr_repository_url
```

### 2) Login, build, tag e push

No PowerShell (ajuste a região se mudar `aws_region`):

```powershell
$REGION = "us-east-1"
$ACCOUNT = (aws sts get-caller-identity --query Account --output text)
$REPO = "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/market-dashboard-backend"

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"

cd ..\backend
docker build -t market-dashboard-backend:latest .
docker tag market-dashboard-backend:latest "${REPO}:latest"
docker push "${REPO}:latest"
```

Ou usando o output do Terraform:

```powershell
$REPO = (terraform -chdir=..\infra output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ($REPO.Split('/')[0])
cd ..\backend
docker build -t market-dashboard-backend:latest .
docker tag market-dashboard-backend:latest "${REPO}:latest"
docker push "${REPO}:latest"
```

### 3) Conferir

```powershell
aws ecr list-images --repository-name market-dashboard-backend --region us-east-1
```

Push é **manual** nesta história (CI/CD = H20).

## H16 — ElastiCache for Valkey

Nó único `cache.t4g.micro` em subnets **privadas**. Security group **sem ingress** (aberto pelas tasks na H19).

```powershell
cd market-dashboard\infra
terraform plan
terraform apply
terraform output valkey_primary_endpoint
terraform output valkey_port
```

Gera **custo contínuo**. Ao fim da sessão: `terraform destroy`.

### IAM (lab / usuario-dados) — bloqueio atual

O Terraform **não consegue** criar ElastiCache sem a action
`elasticache:CreateCacheSubnetGroup`. Isso é permissão IAM, não bug do `.tf`.

Arquivo pronto: `iam-policies/elasticache-study.json`

**Admin** (conta com permissão IAM) anexa ao usuário `usuario-dados`:

```powershell
cd market-dashboard\infra

aws iam put-user-policy `
  --user-name usuario-dados `
  --policy-name MarketDashboardElastiCacheStudy `
  --policy-document file://iam-policies/elasticache-study.json
```

Depois, no usuário do lab:

```powershell
aws sts get-caller-identity
terraform apply
terraform output valkey_primary_endpoint
```

Sem essa policy, `valkey_primary_endpoint` **não existe no state** (apply não concluiu).

## H17 — ECS Fargate (BFF + worker + beat)

**Pré-requisito:** imagem `latest` no ECR (H15).

```powershell
cd market-dashboard\infra
terraform plan
terraform apply
terraform output alb_dns_name
curl.exe -i "http://$(terraform output -raw alb_dns_name)/api/dashboard"
curl.exe -i "http://$(terraform output -raw alb_dns_name)/health"
```

- Beat: `desired_count = 1` (não aumentar).
- Tasks em subnet pública com IP público (sem NAT).
- Logs: `/ecs/market-dashboard/{bff,worker,beat}` no CloudWatch.

Custo: ALB + Fargate + Valkey. Ao fim: `terraform destroy`.
