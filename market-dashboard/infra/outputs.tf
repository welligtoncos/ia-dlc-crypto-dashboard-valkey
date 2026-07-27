output "vpc_id" {
  description = "ID da VPC."
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR da VPC."
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs das subnets públicas (Fargate com IP público nas próximas histórias)."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs das subnets privadas (ElastiCache nas próximas histórias)."
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "ID do Internet Gateway."
  value       = aws_internet_gateway.main.id
}

output "public_route_table_id" {
  description = "ID da route table pública."
  value       = aws_route_table.public.id
}

output "private_route_table_id" {
  description = "ID da route table privada."
  value       = aws_route_table.private.id
}

output "aws_region" {
  description = "Região usada pelo provider."
  value       = var.aws_region
}

output "ecr_repository_url" {
  description = "URL do repositório ECR do backend (build/tag/push)."
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_repository_arn" {
  description = "ARN do repositório ECR do backend."
  value       = aws_ecr_repository.backend.arn
}

output "ecr_repository_name" {
  description = "Nome do repositório ECR."
  value       = aws_ecr_repository.backend.name
}
