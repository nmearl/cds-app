# Staging Target Groups
resource "aws_lb_target_group" "cds_portal_staging" {
  name        = "${var.environment}-portal-staging-tg"
  port        = 8865
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 60
    matcher             = "200"
    path                = "/"
    port                = "8865"
    protocol            = "HTTP"
    timeout             = 30
    unhealthy_threshold = 2
  }
}

resource "aws_lb_target_group" "cds_hubble_staging" {
  name        = "${var.environment}-hubble-staging-tg"
  port        = 8765
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200,307"
    path                = "/hubbles-law"
    port                = "8765"
    protocol            = "HTTP"
    timeout             = 30
    unhealthy_threshold = 2
  }
}

# ALB Listener Rules — host-header routing to staging TGs
# Priority 10/11 are higher priority than the prod rules (100)
resource "aws_lb_listener_rule" "cds_portal_staging_https" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.cds_portal_staging.arn
  }

  condition {
    host_header {
      values = [var.staging_domain_name]
    }
  }
}

resource "aws_lb_listener_rule" "cds_hubble_staging_https" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 11

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.cds_hubble_staging.arn
  }

  condition {
    host_header {
      values = [var.staging_domain_name]
    }
  }

  condition {
    path_pattern {
      values = ["/hubbles-law*"]
    }
  }
}

# Secrets for staging (separate from prod so you can use different OAuth apps, API keys, etc.)
resource "aws_secretsmanager_secret" "cds_portal_staging_secrets" {
  name        = "${var.environment}/cds-portal-staging/secrets"
  description = "Secrets for CDS Portal staging"
}

resource "aws_secretsmanager_secret" "cds_hubble_staging_secrets" {
  name        = "${var.environment}/cds-hubble-staging/secrets"
  description = "Secrets for CDS Hubble staging"
}

# Staging Task Definitions — smaller footprint than prod
resource "aws_ecs_task_definition" "cds_portal_staging" {
  family                   = "${var.environment}-cds-portal-staging"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name  = "cds-portal"
    image = "${aws_ecr_repository.cds_portal.repository_url}:staging"
    portMappings = [{ containerPort = 8865, protocol = "tcp" }]
    essential = true
    secrets = [
      { name = "SOLARA_SESSION_SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.cds_portal_staging_secrets.arn}:SOLARA_SESSION_SECRET_KEY::" },
      # ... mirror the prod secrets block but referencing staging secret ARN
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.cds_portal_staging.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "cds_hubble_staging" {
  family                   = "${var.environment}-cds-hubble-staging"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512   # lighter than prod's 1024
  memory                   = 1024  # lighter than prod's 2048
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name  = "cds-hubble"
    image = "${aws_ecr_repository.cds_hubble.repository_url}:staging"
    portMappings = [{ containerPort = 8765, protocol = "tcp" }]
    essential = true
    secrets = [
      # ... mirror prod secrets block referencing staging secret ARN
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.cds_hubble_staging.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# Staging ECS Services — fixed at 1 task each, no autoscaling needed
resource "aws_ecs_service" "cds_portal_staging" {
  name            = "${var.environment}-cds-portal-staging"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.cds_portal_staging.arn
  desired_count   = 1

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"  # cost savings for staging
    base              = 1
    weight            = 1
  }

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.public[*].id
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.cds_portal_staging.arn
    container_name   = "cds-portal"
    container_port   = 8865
  }

  depends_on = [aws_lb_listener.https]
}

resource "aws_ecs_service" "cds_hubble_staging" {
  name            = "${var.environment}-cds-hubble-staging"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.cds_hubble_staging.arn
  desired_count   = 1

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    base              = 1
    weight            = 1
  }

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.public[*].id
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.cds_hubble_staging.arn
    container_name   = "cds-hubble"
    container_port   = 8765
  }

  depends_on = [aws_lb_listener.https]
}

# CloudWatch Log Groups for staging
resource "aws_cloudwatch_log_group" "cds_portal_staging" {
  name              = "/ecs/${var.environment}-cds-portal-staging"
  retention_in_days = 3
  log_group_class   = "INFREQUENT_ACCESS"
}

resource "aws_cloudwatch_log_group" "cds_hubble_staging" {
  name              = "/ecs/${var.environment}-cds-hubble-staging"
  retention_in_days = 3
  log_group_class   = "INFREQUENT_ACCESS"
}