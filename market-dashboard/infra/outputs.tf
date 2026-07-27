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

output "valkey_primary_endpoint" {
  description = "Endpoint primario do ElastiCache Valkey (host)."
  value       = aws_elasticache_replication_group.valkey.primary_endpoint_address
}

output "valkey_port" {
  description = "Porta do ElastiCache Valkey."
  value       = aws_elasticache_replication_group.valkey.port
}

output "valkey_security_group_id" {
  description = "SG do Valkey (ingress das tasks Fargate na H17/H19)."
  value       = aws_security_group.valkey.id
}

output "alb_dns_name" {
  description = "DNS publico do ALB (http://<dns>/api/dashboard)."
  value       = aws_lb.bff.dns_name
}

output "alb_url" {
  description = "URL base HTTP do BFF via ALB."
  value       = "http://${aws_lb.bff.dns_name}"
}

output "ecs_cluster_name" {
  description = "Nome do cluster ECS."
  value       = aws_ecs_cluster.main.name
}

output "ecs_tasks_security_group_id" {
  description = "SG das tasks Fargate."
  value       = aws_security_group.ecs_tasks.id
}

output "frontend_bucket_name" {
  description = "Bucket S3 privado do build Angular."
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  description = "ID da distribuicao CloudFront (para invalidacao)."
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_url" {
  description = "URL HTTPS do frontend (dominio padrao CloudFront)."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_domain_name" {
  description = "Domain name da distribuicao CloudFront."
  value       = aws_cloudfront_distribution.frontend.domain_name
}
