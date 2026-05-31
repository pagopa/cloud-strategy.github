# Azure DevOps Pipeline Baseline

Use this reference only when the Azure DevOps umbrella needs more than quick routing.

## Structure

- Use 2-space YAML indentation and meaningful `displayName` values.
- Split complex flows into stages and jobs with explicit dependencies.
- Use templates only when they reduce real duplication or make shared controls easier to maintain.
- Keep path, branch, scheduled, and resource triggers intentional.

## Build And Test

- Pin or name agent images deliberately.
- Cache dependencies only where the cache key is stable and invalidation is understood.
- Publish test results and build artifacts with names that operators can recognize.
- Keep code-quality, dependency, and security checks close to the build stage that owns them.

## Deployment

- Use deployment jobs and environment targeting for environment promotion.
- Require approvals or checks for production-like environments when the repository policy expects them.
- Include rollback or recovery steps when the pipeline performs deployment.
- Keep infrastructure deployment through ARM, Bicep, Terraform, or another owned IaC lane explicit.

## Variables And Secrets

- Use parameters for caller-controlled choices and variable groups for shared configuration.
- Mark sensitive variables as secrets and avoid logging them.
- Prefer Key Vault or managed identity patterns for sensitive configuration.
- Document non-obvious variable purpose in the pipeline or adjacent docs.
