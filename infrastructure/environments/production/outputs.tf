output "alb_dns_name" {
  value = module.app_stack.alb_dns_name
}

output "alb_zone_id" {
  value = module.app_stack.alb_zone_id
}

output "vpc_id" {
  value = module.app_stack.vpc_id
}

output "private_subnet_ids" {
  value = module.app_stack.private_subnet_ids
}

output "public_subnet_ids" {
  value = module.app_stack.public_subnet_ids
}

output "ecs_cluster_name" {
  value = module.app_stack.ecs_cluster_name
}

output "cds_portal_service_name" {
  value = module.app_stack.cds_portal_service_name
}

output "cds_hubble_service_name" {
  value = module.app_stack.cds_hubble_service_name
}

output "cds_portal_secrets_arn" {
  value = module.app_stack.cds_portal_secrets_arn
}

output "cds_hubble_secrets_arn" {
  value = module.app_stack.cds_hubble_secrets_arn
}

output "cloudfront_domain_name" {
  value = module.app_stack.cloudfront_domain_name
}

output "cloudfront_distribution_id" {
  value = module.app_stack.cloudfront_distribution_id
}

output "site_url" {
  value = module.app_stack.site_url
}
