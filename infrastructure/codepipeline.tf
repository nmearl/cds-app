# ECR Repositories
resource "aws_ecr_repository" "cds_portal" {
  name                 = "cds-portal"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.environment}-cds-portal-ecr"
    Environment = var.environment
  }
}

resource "aws_ecr_repository" "cds_hubble" {
  name                 = "cds-hubble"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.environment}-cds-hubble-ecr"
    Environment = var.environment
  }
}

# S3 Bucket for CodePipeline artifacts
resource "aws_s3_bucket" "codepipeline_artifacts" {
  bucket = "${var.environment}-cds-codepipeline-artifacts-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.environment}-codepipeline-artifacts"
    Environment = var.environment
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CodeBuild Service Role
resource "aws_iam_role" "codebuild_role" {
  name = "${var.environment}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-codebuild-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "codebuild_policy" {
  name = "${var.environment}-codebuild-policy"
  role = aws_iam_role.codebuild_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.codepipeline_artifacts.arn}",
          "${aws_s3_bucket.codepipeline_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:RegisterTaskDefinition",
          "ecs:DescribeTaskDefinition"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = aws_iam_role.ecs_task_execution_role.arn
      }
    ]
  })
}

# CodePipeline Service Role
resource "aws_iam_role" "codepipeline_role" {
  name = "${var.environment}-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-codepipeline-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "${var.environment}-codepipeline-policy"
  role = aws_iam_role.codepipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketVersioning",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.codepipeline_artifacts.arn}",
          "${aws_s3_bucket.codepipeline_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "codestar-connections:UseConnection"
        ]
        Resource = aws_codestarconnections_connection.github.arn
      }
    ]
  })
}

# GitHub Connection (requires manual setup in AWS Console)
resource "aws_codestarconnections_connection" "github" {
  name          = "${var.environment}-github-connection"
  provider_type = "GitHub"

  tags = {
    Name        = "${var.environment}-github-connection"
    Environment = var.environment
  }
}

# CodeBuild Projects
resource "aws_codebuild_project" "cds_portal_build" {
  name          = "${var.environment}-cds-portal-build"
  description   = "Build project for CDS Portal"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                      = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                       = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode            = true

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    environment_variable {
      name  = "IMAGE_REPO_NAME"
      value = aws_ecr_repository.cds_portal.name
    }

    environment_variable {
      name  = "IMAGE_TAG"
      value = "latest"
    }

    environment_variable {
      name  = "CONTAINER_NAME"
      value = "cds-portal"
    }

    environment_variable {
      name  = "ECS_CLUSTER_NAME"
      value = aws_ecs_cluster.main.name
    }

    environment_variable {
      name  = "ECS_SERVICE_NAME"
      value = "${var.environment}-cds-portal"
    }
  }

  source {
    type = "CODEPIPELINE"
    buildspec = "buildspec-portal.yml"
  }

  tags = {
    Name        = "${var.environment}-cds-portal-build"
    Environment = var.environment
  }
}

resource "aws_codebuild_project" "cds_hubble_build" {
  name          = "${var.environment}-cds-hubble-build"
  description   = "Build project for CDS Hubble"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                      = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                       = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode            = true

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    environment_variable {
      name  = "IMAGE_REPO_NAME"
      value = aws_ecr_repository.cds_hubble.name
    }

    environment_variable {
      name  = "IMAGE_TAG"
      value = "latest"
    }

    environment_variable {
      name  = "CONTAINER_NAME"
      value = "cds-hubble"
    }

    environment_variable {
      name  = "ECS_CLUSTER_NAME"
      value = aws_ecs_cluster.main.name
    }

    environment_variable {
      name  = "ECS_SERVICE_NAME"
      value = "${var.environment}-cds-hubble"
    }
  }

  source {
    type = "CODEPIPELINE"
    buildspec = "buildspec-hubble.yml"
  }

  tags = {
    Name        = "${var.environment}-cds-hubble-build"
    Environment = var.environment
  }
}

# CodePipeline
resource "aws_codepipeline" "cds_pipeline" {
  name     = "${var.environment}-cds-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.codepipeline_artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = aws_codestarconnections_connection.github.arn
        FullRepositoryId = var.github_repository
        BranchName       = var.github_branch
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build-CDS-Portal"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["portal_build_output"]
      version          = "1"
      run_order        = 1

      configuration = {
        ProjectName = aws_codebuild_project.cds_portal_build.name
      }
    }

    action {
      name             = "Build-CDS-Hubble"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["hubble_build_output"]
      version          = "1"
      run_order        = 1

      configuration = {
        ProjectName = aws_codebuild_project.cds_hubble_build.name
      }
    }
  }

  tags = {
    Name        = "${var.environment}-cds-pipeline"
    Environment = var.environment
  }
}

# Data source for AWS account ID
data "aws_caller_identity" "current" {}

# CloudWatch Log Groups for CodeBuild
resource "aws_cloudwatch_log_group" "codebuild_portal" {
  name              = "/aws/codebuild/${var.environment}-cds-portal-build"
  retention_in_days = 7
  log_group_class   = "INFREQUENT_ACCESS"

  tags = {
    Name        = "${var.environment}-codebuild-portal-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "codebuild_hubble" {
  name              = "/aws/codebuild/${var.environment}-cds-hubble-build"
  retention_in_days = 7
  log_group_class   = "INFREQUENT_ACCESS"

  tags = {
    Name        = "${var.environment}-codebuild-hubble-logs"
    Environment = var.environment
  }
}