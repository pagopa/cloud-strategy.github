---
agent: agent
description: Modify or create Terraform modules for FinOps infrastructure
---

# Terraform Module

## Context

I need to modify or extend Terraform configuration for FinOps infrastructure (dashboards, monitoring).

## Inputs

- **Modification type**: ${input:type:resource,variable,output,data_source,module}
- **Description**: ${input:description}

## Steps

1. Use the `terraform-module` skill in `.github/skills/terraform-module/SKILL.md`.
2. Analyze existing files with `#codebase` and:
   - `#file:aws/dashboard/`
   - `#file:azure/dashboard/`
3. Implement changes following the skill template and repository instructions.

## Validations

- Run `terraform fmt` before committing.
- Check `#problems` for errors after changes.
