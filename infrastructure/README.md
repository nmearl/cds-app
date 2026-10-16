# Terraform Layout

This directory now uses isolated Terraform roots per environment:

- `environments/production`
- `environments/delivery`

`production` provisions its application stack from
`modules/app_stack`, so Terraform state and infrastructure are isolated.

`delivery` provisions the shared ECR repositories and CodePipeline workflow from
`modules/release_pipeline`. The pipeline builds and then deploys to production. 
Its naming prefix is kept aligned with the historical production stack so existing delivery
resources can be migrated without replacement.

## Usage

Run Terraform from the specific environment directory:

```sh
cd infrastructure/environments/deployment
terraform init
cp terraform.tfvars.example terraform.tfvars
terraform plan
```

Repeat the same pattern for `delivery`.

## Migration Notes

- The old top-level Terraform root was removed as the active entry point.
- Existing local state files in `infrastructure/` were left in place as
  historical artifacts and should not be used for future applies.
- Before applying `delivery`, fill in the real ECS cluster and service names
  from the `production` outputs.
