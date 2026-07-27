# ECR (H15) — uma imagem para BFF (Uvicorn), worker e beat (Celery).
# O comando de entrada muda no ECS/Compose; a imagem é a mesma.
#
# Nota: lifecycle policy (PutLifecyclePolicy) foi omitida — a IAM do lab
# (usuario-dados) não permite essa action. Pode ser adicionada depois se a role ganhar a permissão.

resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-backend"
  }
}
