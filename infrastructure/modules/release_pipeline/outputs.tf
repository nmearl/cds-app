output "ecr_repository_cds_portal_url" {
  description = "URL of the CDS Portal ECR repository"
  value       = aws_ecr_repository.cds_portal.repository_url
}

output "ecr_repository_cds_hubble_url" {
  description = "URL of the CDS Hubble ECR repository"
  value       = aws_ecr_repository.cds_hubble.repository_url
}

output "codepipeline_name" {
  description = "Name of the CodePipeline"
  value       = aws_codepipeline.cds_pipeline.name
}

output "github_connection_arn" {
  description = "ARN of the GitHub connection"
  value       = aws_codestarconnections_connection.github.arn
}
