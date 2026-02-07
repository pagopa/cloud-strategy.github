---
name: terraform-feature
description: Add or modify Terraform resources, variables, outputs, and data sources.
---

# Terraform Feature Skill

## When to use
- Add or modify resources.
- Add/update variables and outputs.
- Add data sources.

## Mandatory rules
- Preserve naming and folder conventions.
- Use `snake_case` for Terraform identifiers.
- Add `description` and `type` to variables.
- Add `description` to outputs.
- Avoid hardcoded values.
- Apply tags where supported.

## Validation
- `terraform fmt`
- `terraform validate`
- Review `terraform plan`
