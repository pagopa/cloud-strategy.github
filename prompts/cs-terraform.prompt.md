---
description: Create or modify Terraform resources and features
name: cs-terraform
agent: agent
argument-hint: action=<create|modify> type=<resource|module|variable|output|data_source> description=<text> target_dir=<path>
---

# Terraform Task

## Context
Create or modify Terraform resources, modules, variables, outputs, or data sources while preserving module consistency.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Task type**: ${input:type:resource,module,variable,output,data_source}
- **Description**: ${input:description}
- **Target directory**: ${input:target_dir}

## Instructions

1. Use the skill in `.github/skills/terraform-feature/SKILL.md`.
2. Search existing `.tf` files in the target directory.
3. Follow existing naming conventions and patterns.
4. Apply the task with:
   - correct naming (`snake_case`)
   - `description` for variables/outputs
   - no hardcoded values
   - tags where supported
5. Keep technical output and documentation in English.

## Validation
- Run `terraform fmt`.
- Run `terraform validate`.
- Check errors in `terraform plan`.
