output "ecr_repository_cds_portal_url" {
  value = module.release_pipeline.ecr_repository_cds_portal_url
}

output "ecr_repository_cds_hubble_url" {
  value = module.release_pipeline.ecr_repository_cds_hubble_url
}

output "codepipeline_name" {
  value = module.release_pipeline.codepipeline_name
}

output "github_connection_arn" {
  value = module.release_pipeline.github_connection_arn
}
