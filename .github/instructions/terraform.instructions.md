---
description: Terraform authoring standards for readability, typed interfaces, and validation-first delivery.
applyTo: "**/*.tf"
---

# Terraform Instructions

## Formatting
- Run `terraform fmt` before commit.
- Use 2-space indentation.
- Use `tfenv` (or repository equivalent) for Terraform version management.

## Naming conventions
- Resources: `snake_case` (for example `aws_iam_role.lambda_execution`).
- Variables: `snake_case` with `description`.
- Locals: `snake_case`, grouped by domain. Avoid using locals for hardcoded variables.

## Variables and Values (Non-Module code)
- Avoid using `default` values in variables as much as possible (except for Terraform modules).
- Configuration values must be defined in `.tfvars` files.
- For resources configurations, use direct hardcoded values in the code unless they change per environment (and thus require a variable).
- These rules do not apply to reusable standalone modules.

## Structure
- Always add `description` to variables.
- Use type constraints for variables.
- Prefer `for_each` over `count` when logical keys matter.
- Prefer data sources over hardcoded IDs.
- Keep backend/state configuration explicit and consistent with repository standards.
- Ensure state locking is enabled when supported by the backend.
- Keep workspace/environment separation explicit.

## Lifecycle and safety
- Use `prevent_destroy` for critical resources when appropriate.
- Use `create_before_destroy` for replacement-sensitive resources.
- Use `ignore_changes` only with documented rationale.

## Multi-cloud baseline
- Pin provider versions in `required_providers`.
- Pin external module sources to exact versions or immutable refs.
- For registry modules, prefer exact `version = "= x.y.z"` constraints over floating ranges.
- For git-based module sources, use immutable `?ref=` values and add a short comment with the corresponding release/tag when known.
- Keep provider configuration explicit for region/subscription/project scope.
- Reuse repository-specific provider conventions for AWS, Azure, and GCP.

## Validation
- Run `terraform validate` after changes.
- Review `terraform plan` before apply.
