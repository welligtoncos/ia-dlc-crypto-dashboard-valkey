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
