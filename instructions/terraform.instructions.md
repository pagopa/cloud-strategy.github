---
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
- Locals: `snake_case`, grouped by domain.

## Structure
- Always add `description` to variables.
- Use type constraints for variables.
- Prefer `for_each` over `count` when logical keys matter.
- Prefer data sources over hardcoded IDs.

## Validation
- Run `terraform validate` after changes.
- Review `terraform plan` before apply.
