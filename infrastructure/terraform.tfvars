aws_region = "us-east-1"
environment = "production"
cds_portal_image = "072415053150.dkr.ecr.us-east-1.amazonaws.com/cds-portal:latest"
cds_hubble_image = "072415053150.dkr.ecr.us-east-1.amazonaws.com/cds-hubble:latest"

# Auto-scaling configuration
cds_portal_min_capacity = 1
cds_portal_max_capacity = 3
cds_hubble_min_capacity = 2
cds_hubble_max_capacity = 4

# GitHub repository for CI/CD
github_repository = "nmearl/cds-app"
github_branch = "main"

# ALB domain name for SSL certificate
alb_domain_name = "app.cosmicds.cfa.harvard.edu"