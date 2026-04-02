#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OLD_STATE="$ROOT_DIR/terraform.tfstate"
OLD_BACKUP="$ROOT_DIR/terraform.tfstate.backup"
STATE_ROOT="$ROOT_DIR/.terraform-state"
PROD_STATE="$STATE_ROOT/production/terraform.tfstate"
DELIVERY_STATE="$STATE_ROOT/delivery/terraform.tfstate"
LEGACY_STATE="$STATE_ROOT/legacy-orphans/terraform.tfstate"

if [[ ! -f "$OLD_STATE" ]]; then
  echo "Old state file not found: $OLD_STATE" >&2
  exit 1
fi

if [[ -f "$PROD_STATE" || -f "$DELIVERY_STATE" || -f "$LEGACY_STATE" ]]; then
  echo "Refusing to overwrite existing migrated state files in $STATE_ROOT" >&2
  exit 1
fi

mkdir -p "$STATE_ROOT/production" "$STATE_ROOT/delivery" "$STATE_ROOT/legacy-orphans"

STAMP="$(date +%Y%m%d-%H%M%S)"
cp "$OLD_STATE" "$STATE_ROOT/legacy-root-pre-migration-$STAMP.tfstate"
if [[ -f "$OLD_BACKUP" ]]; then
  cp "$OLD_BACKUP" "$STATE_ROOT/legacy-root-pre-migration-$STAMP.tfstate.backup"
fi

mv_object() {
  local source_addr="$1"
  local target_addr="$2"
  local target_state="$3"

  terraform state mv -state="$OLD_STATE" -state-out="$target_state" "$source_addr" "$target_addr" >/dev/null
  echo "moved $source_addr -> $target_addr"
}

while IFS='|' read -r src dst; do
  mv_object "$src" "$dst" "$PROD_STATE"
done <<'EOF'
data.aws_acm_certificate.alb|module.app_stack.data.aws_acm_certificate.site
data.aws_availability_zones.available|module.app_stack.data.aws_availability_zones.available
aws_appautoscaling_policy.cds_hubble_cpu|module.app_stack.aws_appautoscaling_policy.cds_hubble_cpu[0]
aws_appautoscaling_policy.cds_portal_cpu|module.app_stack.aws_appautoscaling_policy.cds_portal_cpu[0]
aws_appautoscaling_target.cds_hubble|module.app_stack.aws_appautoscaling_target.cds_hubble[0]
aws_appautoscaling_target.cds_portal|module.app_stack.aws_appautoscaling_target.cds_portal[0]
aws_cloudfront_distribution.apps|module.app_stack.aws_cloudfront_distribution.apps
aws_cloudwatch_log_group.cds_hubble|module.app_stack.aws_cloudwatch_log_group.cds_hubble
aws_cloudwatch_log_group.cds_portal|module.app_stack.aws_cloudwatch_log_group.cds_portal
aws_ecs_cluster.main|module.app_stack.aws_ecs_cluster.main
aws_ecs_service.cds_hubble|module.app_stack.aws_ecs_service.cds_hubble
aws_ecs_service.cds_portal|module.app_stack.aws_ecs_service.cds_portal
aws_ecs_task_definition.cds_hubble|module.app_stack.aws_ecs_task_definition.cds_hubble
aws_ecs_task_definition.cds_portal|module.app_stack.aws_ecs_task_definition.cds_portal
aws_iam_role.ecs_task_execution_role|module.app_stack.aws_iam_role.ecs_task_execution_role
aws_iam_role_policy.ecs_secrets_policy|module.app_stack.aws_iam_role_policy.ecs_secrets_policy
aws_iam_role_policy_attachment.ecs_task_execution_role_policy|module.app_stack.aws_iam_role_policy_attachment.ecs_task_execution_role_policy
aws_internet_gateway.main|module.app_stack.aws_internet_gateway.main
aws_lb.main|module.app_stack.aws_lb.main
aws_lb_listener.https|module.app_stack.aws_lb_listener.https
aws_lb_listener.main|module.app_stack.aws_lb_listener.http
aws_lb_listener_rule.cds_hubble_https|module.app_stack.aws_lb_listener_rule.cds_hubble_https
aws_lb_target_group.cds_hubble|module.app_stack.aws_lb_target_group.cds_hubble
aws_lb_target_group.cds_portal|module.app_stack.aws_lb_target_group.cds_portal
aws_route_table.public|module.app_stack.aws_route_table.public
aws_route_table_association.public[0]|module.app_stack.aws_route_table_association.public[0]
aws_route_table_association.public[1]|module.app_stack.aws_route_table_association.public[1]
aws_secretsmanager_secret.cds_hubble_secrets|module.app_stack.aws_secretsmanager_secret.cds_hubble_secrets
aws_secretsmanager_secret.cds_portal_secrets|module.app_stack.aws_secretsmanager_secret.cds_portal_secrets
aws_security_group.alb|module.app_stack.aws_security_group.alb
aws_security_group.ecs_tasks|module.app_stack.aws_security_group.ecs_tasks
aws_ssm_parameter.cds_hubble_env_vars["LOG_LEVEL"]|module.app_stack.aws_ssm_parameter.cds_hubble_env_vars["LOG_LEVEL"]
aws_ssm_parameter.cds_hubble_env_vars["NODE_ENV"]|module.app_stack.aws_ssm_parameter.cds_hubble_env_vars["NODE_ENV"]
aws_ssm_parameter.cds_portal_env_vars["LOG_LEVEL"]|module.app_stack.aws_ssm_parameter.cds_portal_env_vars["LOG_LEVEL"]
aws_ssm_parameter.cds_portal_env_vars["NODE_ENV"]|module.app_stack.aws_ssm_parameter.cds_portal_env_vars["NODE_ENV"]
aws_subnet.private[0]|module.app_stack.aws_subnet.private[0]
aws_subnet.private[1]|module.app_stack.aws_subnet.private[1]
aws_subnet.public[0]|module.app_stack.aws_subnet.public[0]
aws_subnet.public[1]|module.app_stack.aws_subnet.public[1]
aws_vpc.main|module.app_stack.aws_vpc.main
EOF

while IFS='|' read -r src dst; do
  mv_object "$src" "$dst" "$DELIVERY_STATE"
done <<'EOF'
data.aws_caller_identity.current|module.release_pipeline.data.aws_caller_identity.current
aws_cloudwatch_log_group.codebuild_hubble|module.release_pipeline.aws_cloudwatch_log_group.codebuild_hubble
aws_cloudwatch_log_group.codebuild_portal|module.release_pipeline.aws_cloudwatch_log_group.codebuild_portal
aws_codebuild_project.cds_hubble_build|module.release_pipeline.aws_codebuild_project.cds_hubble_build
aws_codebuild_project.cds_portal_build|module.release_pipeline.aws_codebuild_project.cds_portal_build
aws_codepipeline.cds_pipeline|module.release_pipeline.aws_codepipeline.cds_pipeline
aws_codestarconnections_connection.github|module.release_pipeline.aws_codestarconnections_connection.github
aws_ecr_repository.cds_hubble|module.release_pipeline.aws_ecr_repository.cds_hubble
aws_ecr_repository.cds_portal|module.release_pipeline.aws_ecr_repository.cds_portal
aws_iam_role.codebuild_role|module.release_pipeline.aws_iam_role.codebuild_role
aws_iam_role.codepipeline_role|module.release_pipeline.aws_iam_role.codepipeline_role
aws_iam_role_policy.codebuild_policy|module.release_pipeline.aws_iam_role_policy.codebuild_policy
aws_iam_role_policy.codepipeline_policy|module.release_pipeline.aws_iam_role_policy.codepipeline_policy
aws_s3_bucket.codepipeline_artifacts|module.release_pipeline.aws_s3_bucket.codepipeline_artifacts
aws_s3_bucket_public_access_block.codepipeline_artifacts|module.release_pipeline.aws_s3_bucket_public_access_block.codepipeline_artifacts
aws_s3_bucket_server_side_encryption_configuration.codepipeline_artifacts|module.release_pipeline.aws_s3_bucket_server_side_encryption_configuration.codepipeline_artifacts
aws_s3_bucket_versioning.codepipeline_artifacts|module.release_pipeline.aws_s3_bucket_versioning.codepipeline_artifacts
random_string.bucket_suffix|module.release_pipeline.random_string.bucket_suffix
EOF

cp "$OLD_STATE" "$LEGACY_STATE"

echo
echo "Migration complete."
echo "Production state: $PROD_STATE"
echo "Delivery state:   $DELIVERY_STATE"
echo "Legacy orphans:   $LEGACY_STATE"
echo
echo "Remaining legacy addresses:"
terraform state list -state="$LEGACY_STATE"
