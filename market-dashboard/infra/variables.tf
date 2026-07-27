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
