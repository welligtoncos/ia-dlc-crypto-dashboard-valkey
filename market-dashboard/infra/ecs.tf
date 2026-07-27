# ECS Fargate — BFF (ALB) + worker + beat (H17)
# Trade-off H14: tasks em subnet PUBLICA com assign_public_ip (sem NAT).
# Beat: desired_count = 1 (nunca subir 2 beats).
# Mesma imagem ECR; so muda o command.

locals {
  backend_image = "${aws_ecr_repository.backend.repository_url}:${var.backend_image_tag}"

  celery_broker_url = "redis://${aws_elasticache_replication_group.valkey.primary_endpoint_address}:${aws_elasticache_replication_group.valkey.port}/0"

  common_environment = [
    { name = "VALKEY_HOST", value = aws_elasticache_replication_group.valkey.primary_endpoint_address },
    { name = "VALKEY_PORT", value = tostring(aws_elasticache_replication_group.valkey.port) },
    { name = "VALKEY_DB", value = "0" },
    { name = "CELERY_BROKER_URL", value = local.celery_broker_url },
    { name = "CELERY_RESULT_BACKEND", value = local.celery_broker_url },
    { name = "DASHBOARD_COIN_IDS", value = var.dashboard_coin_ids },
    { name = "BEAT_INTERVAL_SECONDS", value = tostring(var.beat_interval_seconds) },
    { name = "CACHE_TTL_SECONDS", value = tostring(var.cache_ttl_seconds) },
  ]
}

# --- CloudWatch Logs ---

resource "aws_cloudwatch_log_group" "bff" {
  name              = "/ecs/${var.project_name}/bff"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}/worker"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "beat" {
  name              = "/ecs/${var.project_name}/beat"
  retention_in_days = 7
}

# --- IAM (execution + task) ---

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${var.project_name}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name               = "${var.project_name}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

# --- Security groups ---

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb"
  description = "ALB HTTP 80 from internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All egress"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-alb-sg"
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks"
  description = "Fargate tasks - BFF port from ALB only"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "BFF container from ALB"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "All egress (CoinGecko, ECR, Valkey)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs-tasks-sg"
  }
}

# H17 minimo: Valkey aceita 6379 so do SG das tasks (H19 revisita amarração).
resource "aws_security_group_rule" "valkey_from_ecs_tasks" {
  type                     = "ingress"
  description              = "Valkey from Fargate tasks"
  from_port                = var.valkey_port
  to_port                  = var.valkey_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.valkey.id
  source_security_group_id = aws_security_group.ecs_tasks.id
}

# --- ALB ---

resource "aws_lb" "bff" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name = "${var.project_name}-alb"
  }
}

resource "aws_lb_target_group" "bff" {
  name        = "${var.project_name}-bff-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${var.project_name}-bff-tg"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.bff.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.bff.arn
  }
}

# --- ECS cluster ---

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  tags = {
    Name = "${var.project_name}-cluster"
  }
}

# --- Task definitions ---

resource "aws_ecs_task_definition" "bff" {
  family                   = "${var.project_name}-bff"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "bff"
      image     = local.backend_image
      essential = true
      command   = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", tostring(var.container_port)]
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      environment = local.common_environment
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.bff.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "bff"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = local.backend_image
      essential = true
      command   = ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
      environment = local.common_environment
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "beat" {
  family                   = "${var.project_name}-beat"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "beat"
      image     = local.backend_image
      essential = true
      # schedule em /tmp: filesystem do container e efemero/read-mostly
      command = [
        "celery", "-A", "celery_app", "beat",
        "--loglevel=info",
        "--schedule=/tmp/celerybeat-schedule"
      ]
      environment = local.common_environment
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.beat.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "beat"
        }
      }
    }
  ])
}

# --- Services ---

resource "aws_ecs_service" "bff" {
  name            = "${var.project_name}-bff"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.bff.arn
  desired_count   = var.bff_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.bff.arn
    container_name   = "bff"
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }
}

resource "aws_ecs_service" "beat" {
  name            = "${var.project_name}-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.beat.arn
  desired_count   = 1 # EXATAMENTE 1 — dois beats duplicam o schedule
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }
}
