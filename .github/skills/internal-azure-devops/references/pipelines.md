# Azure DevOps Pipeline Baseline

Use this reference for Azure DevOps pipeline authoring and review. Route
tool-neutral delivery strategy to `/internal-devops-core-principles`.

## Structure and triggers

- Use 2-space YAML indentation and meaningful `displayName` values.
- Split complex flows into stages and jobs with explicit `dependsOn` so a
  failure points to the owning build, test, package, or deploy stage.
- Keep branch, path, scheduled (`schedules`), and pipeline or repository
  resource triggers intentional; avoid `trigger: '*'` without path filters.
- Use `extends` or `template` references when they reduce duplication or
  centralize shared controls. Pin remote template repositories to a ref.
- Use `parameters` for caller-controlled choices and variable groups for
  shared configuration.

## Tasks, pools, and artifacts

- Pin task major versions (for example `AzureCLI@2`) and name agent pools and
  images deliberately instead of relying on floating `-latest` images for
  release builds.
- Cache dependencies only when the key is stable and invalidation is clear.
- Publish test results and pipeline artifacts with recognizable names and
  explicit retention when downstream stages consume them.
- Set `timeoutInMinutes` on long or risky jobs.

## Deployment

- Use `deployment` jobs that target an `environment` for promotion.
- Protect production-like environments with approvals and checks, such as
  required approvers, branch control, business hours, or exclusive lock.
- Include health checks and a rollback or redeploy-previous strategy in
  deployment jobs.
- Make infrastructure deployment through ARM, Bicep, Terraform, or another
  repository-owned mechanism explicit.

## Service connections, variables, and secrets

- Scope Azure Resource Manager service connections to the narrowest
  subscription or resource group and prefer workload identity federation over
  secrets.
- Restrict service connection and variable group use to the pipelines that
  need them through pipeline permissions.
- Mark sensitive variables as secret, or link variable groups to Key Vault.
  Never echo secret values.
- Document non-obvious variable purpose in the pipeline or adjacent
  repository documentation.
