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
