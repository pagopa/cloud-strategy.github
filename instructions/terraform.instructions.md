---
applyTo: "**/*.tf"
---

# Terraform Instructions

## Formatting
- Run `terraform fmt` before committing
- Use 2 spaces for indentation
- Use `tfenv` for version management

## Naming Conventions
- Resources: `snake_case` (e.g., `aws_iam_role.lambda_execution`)
- Variables: `snake_case` with descriptions
- Locals: `snake_case`, group related values

## Structure
- Always add `description` to variables
- Use `type` constraints for variables
- Prefer `for_each` over `count` for resources
- Use data sources instead of hardcoded IDs

## Validation
- Run `terraform validate` after changes
- Check `terraform plan` output before applying
