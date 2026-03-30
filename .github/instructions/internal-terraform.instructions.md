---
description: Terraform authoring standards for readability, typed interfaces, and validation-first delivery.
applyTo: "**/*.tf"
---

# Terraform Instructions

## Formatting
- Run `terraform fmt` before commit.
- Use 2-space indentation.
- Use `tfenv` (or repository equivalent) for Terraform version management.
- Keep related resources grouped in predictable files such as `providers.tf`, `variables.tf`, `outputs.tf`, and domain-specific resource files.
- Place `depends_on`, `for_each` or `count` early in the resource block, and keep `lifecycle` near the end.

## Naming conventions
- Resources: `snake_case` (for example `aws_iam_role.lambda_execution`).
- Variables: `snake_case` with `description`.
- Locals: `snake_case`, grouped by domain. Avoid using locals for hardcoded variables.
- Use clear output names and add `description` to outputs as well as variables.

## Variables and Values (Non-Module code)
- Avoid using `default` values in variables as much as possible (except for Terraform modules).
- Configuration values must be defined in `.tfvars` files.
- For resources configurations, use direct hardcoded values in the code unless they change per environment (and thus require a variable).
- These rules do not apply to reusable standalone modules.
- Mark truly sensitive variables and outputs with `sensitive = true`.
- Never commit credentials, tokens, certificates, secrets, or Terraform state to version control.

## Structure
- Always add `description` to variables.
- Use type constraints for variables.
- Prefer `for_each` over `count` when logical keys matter.
- Prefer data sources over hardcoded IDs.
- Avoid unnecessary data sources for resources managed in the same configuration; use outputs or direct references instead.
- Use modules to encapsulate related resources, but avoid modules that wrap a single trivial resource or create unnecessary nesting.
- Keep backend/state configuration explicit and consistent with repository standards.
- Ensure state locking is enabled when supported by the backend.
- Keep workspace/environment separation explicit.
- Use outputs to expose information needed by other modules or operators without leaking sensitive values.

## Lifecycle and safety
- Use `prevent_destroy` for critical resources when appropriate.
- Use `create_before_destroy` for replacement-sensitive resources.
- Use `ignore_changes` only with documented rationale.
- Prefer least-privilege IAM/RBAC and narrow network exposure in the infrastructure being declared.
- Enable encryption at rest and in transit when the platform supports it.

## Multi-cloud baseline
- Pin provider versions in `required_providers`.
- Pin external module sources to exact versions or immutable refs.
- For registry modules, prefer exact `version = "= x.y.z"` constraints over floating ranges.
- For git-based module sources, use immutable `?ref=` values and add a short comment with the corresponding release/tag when known.
- Keep provider configuration explicit for region/subscription/project scope.
- Reuse repository-specific provider conventions for AWS, Azure, and GCP.

## Documentation and testing
- Document non-obvious design decisions with concise comments near the configuration they justify.
- Use `terraform-docs` when the module or project already relies on generated Terraform documentation.
- Use `.tftest.hcl` tests when the repository or module includes Terraform native tests.

## Validation
- Run `terraform validate` after changes.
- Run `tflint` when available for the target project.
- Review `terraform plan` before apply.
