output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "cds_portal_service_name" {
  description = "Name of the CDS Portal ECS service"
  value       = aws_ecs_service.cds_portal.name
}

output "cds_hubble_service_name" {
  description = "Name of the CDS Hubble ECS service"
  value       = aws_ecs_service.cds_hubble.name
}

output "cds_portal_secrets_arn" {
  description = "ARN of the CDS Portal secret"
  value       = aws_secretsmanager_secret.cds_portal_secrets.arn
}

output "cds_hubble_secrets_arn" {
  description = "ARN of the CDS Hubble secret"
  value       = aws_secretsmanager_secret.cds_hubble_secrets.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.apps.domain_name
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.apps.id
}

output "site_url" {
  description = "Primary HTTPS URL for this environment"
  value       = "https://${var.site_domain_name}"
}
