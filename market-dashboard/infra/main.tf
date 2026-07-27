# Fundação Terraform — Market Dashboard (H14)
#
# State: LOCAL por padrão (adequado a estudo).
# Para migrar para state remoto (equipe / CI):
#   1) Crie bucket S3 (versionamento) + tabela DynamoDB (LockID) fora deste stack, ou via bootstrap.
#   2) Descomente o bloco backend "s3" abaixo e rode:
#        terraform init -migrate-state
#
# terraform {
#   backend "s3" {
#     bucket         = "SEU-BUCKET-TFSTATE"
#     key            = "market-dashboard/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "SEU-LOCK-TABLE"
#     encrypt        = true
#   }
# }

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}
