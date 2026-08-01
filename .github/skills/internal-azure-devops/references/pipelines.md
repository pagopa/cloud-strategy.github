# Azure DevOps Pipeline Baseline

Use this reference for detailed pipeline authoring and review.

## Structure and triggers

- Use 2-space YAML indentation and meaningful `displayName` values.
- Split complex flows into stages and jobs with explicit dependencies.
- Keep branch, path, scheduled, and resource triggers intentional.
- Use templates when they reduce duplication or centralize shared controls.

## Build and test

- Pin or name agent images deliberately.
- Cache dependencies only when the key is stable and invalidation is clear.
- Publish test results and build artifacts with recognizable names.
- Keep code-quality, dependency, and security checks near the owning build
  stage.

## Deployment

- Use deployment jobs and environment targeting for promotion.
- Require approvals or checks for production-like environments when repository
  policy expects them.
- Include rollback, recovery, and health-check steps for deployment pipelines.
- Make infrastructure deployment through ARM, Bicep, Terraform, or another
  repository-owned mechanism explicit.

## Variables and secrets

- Use parameters for caller-controlled choices and variable groups for shared
  configuration.
- Mark sensitive variables as secrets and avoid logging them.
- Prefer Key Vault or managed identity patterns for sensitive configuration.
- Document non-obvious variable purpose in the pipeline or adjacent repository
  documentation.
