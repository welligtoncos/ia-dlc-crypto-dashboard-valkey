# ElastiCache for Valkey (H16)
# - Valkey na AWS usa Replication Group (CreateReplicationGroup), nao Cache Cluster.
# - No unico cache.t4g.micro (estudo; sem replicas / cluster mode)
# - Subnets privadas; SG sem ingress (H19 libera tasks ECS)
# Custo continuo enquanto existir — terraform destroy ao fim da sessao.

resource "aws_elasticache_subnet_group" "valkey" {
  name       = "${var.project_name}-valkey"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-valkey-subnets"
  }
}

resource "aws_security_group" "valkey" {
  name        = "${var.project_name}-valkey"
  # EC2 GroupDescription: ASCII only (no accents / em-dash).
  description = "Valkey ElastiCache - no public ingress; H19 adds task SG rules"
  vpc_id      = aws_vpc.main.id

  # Sem blocos ingress de proposito (SG inicia fechado).

  egress {
    description = "Allow all egress"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-valkey-sg"
  }
}

resource "aws_elasticache_replication_group" "valkey" {
  replication_group_id = "${var.project_name}-vk"
  description          = "Valkey single-node study (H16)"

  engine               = "valkey"
  engine_version       = var.valkey_engine_version
  node_type            = var.valkey_node_type
  port                 = var.valkey_port
  parameter_group_name = var.valkey_parameter_group

  num_cache_clusters         = 1
  automatic_failover_enabled = false
  multi_az_enabled           = false

  subnet_group_name  = aws_elasticache_subnet_group.valkey.name
  security_group_ids = [aws_security_group.valkey.id]

  apply_immediately = true

  tags = {
    Name = "${var.project_name}-valkey"
  }
}
