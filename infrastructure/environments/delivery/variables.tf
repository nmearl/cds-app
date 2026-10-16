variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Name prefix for shared delivery resources"
  type        = string
  default     = "production"
}

variable "github_repository" {
  description = "GitHub repository in the format owner/repo"
  type        = string
  default     = "nmearl/cds-app"
}

variable "github_branch" {
  description = "GitHub branch to track for changes"
  type        = string
  default     = "main"
}

variable "approval_notification_arn" {
  description = "SNS topic ARN for approval notifications"
  type        = string
  default     = ""
}

variable "hubble_repository_name" {
  description = "ECR repository name for cds-hubble"
  type        = string
  default     = "cds-hubble"
}

variable "codebuild_log_retention_days" {
  description = "Retention in days for delivery CodeBuild CloudWatch log groups"
  type        = number
  default     = 7
}

variable "production_cluster_name" {
  description = "Production ECS cluster name"
  type        = string
}

variable "production_hubble_service_name" {
  description = "Production hubble ECS service name"
  type        = string
}
