variable "aws_region" {
  description = "Região AWS onde a rede e os demais recursos serão criados."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefixo de nomes/tags dos recursos."
  type        = string
  default     = "market-dashboard"
}

variable "environment" {
  description = "Ambiente lógico (ex.: study, dev)."
  type        = string
  default     = "study"
}

variable "vpc_cidr" {
  description = "CIDR da VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDRs das subnets públicas (uma por AZ; mínimo 2)."
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDRs das subnets privadas (uma por AZ; mínimo 2)."
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "AZs a usar (tamanho deve coincidir com as listas de CIDR)."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# --- H16 ElastiCache Valkey ---

variable "valkey_node_type" {
  description = "Tipo do nó ElastiCache (mais barato para estudo)."
  type        = string
  default     = "cache.t4g.micro"
}

variable "valkey_engine_version" {
  description = "Versão do engine Valkey."
  type        = string
  default     = "8.0"
}

variable "valkey_parameter_group" {
  description = "Parameter group default do Valkey."
  type        = string
  default     = "default.valkey8"
}

variable "valkey_port" {
  description = "Porta do Valkey."
  type        = number
  default     = 6379
}

# --- H17 ECS Fargate ---

variable "backend_image_tag" {
  description = "Tag da imagem no ECR (push manual na H15)."
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Porta HTTP do BFF (Uvicorn)."
  type        = number
  default     = 8000
}

variable "fargate_cpu" {
  description = "CPU units Fargate (256 = 0.25 vCPU)."
  type        = string
  default     = "256"
}

variable "fargate_memory" {
  description = "Memoria Fargate em MiB."
  type        = string
  default     = "512"
}

variable "bff_desired_count" {
  description = "Replicas do BFF (1-2 no estudo)."
  type        = number
  default     = 1
}

variable "worker_desired_count" {
  description = "Replicas do worker Celery."
  type        = number
  default     = 1
}

variable "dashboard_coin_ids" {
  description = "Lista de moedas (env DASHBOARD_COIN_IDS)."
  type        = string
  default     = "bitcoin,ethereum,solana"
}

variable "beat_interval_seconds" {
  description = "Intervalo do Celery Beat."
  type        = number
  default     = 60
}

variable "cache_ttl_seconds" {
  description = "TTL do cache de indicadores."
  type        = number
  default     = 60
}
