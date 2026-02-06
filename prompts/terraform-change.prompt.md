---
description: Add or modify Terraform resources and features
name: terraform-change
agent: agent
---

# Terraform Change

## Context
Add or modify Terraform resources, variables, outputs, or data sources.

## Required Inputs
- **Change type**: ${input:type:resource,variable,output,data_source}
- **Description**: ${input:description}
- **Target directory**: ${input:target_dir}

## Instructions

1. Use the skill in `.github/skills/terraform-feature/SKILL.md`
2. Search existing `.tf` files in the target directory
3. Follow existing naming conventions and patterns
4. Apply the change with:
   - Proper naming (snake_case)
   - Descriptions for variables/outputs
   - No hardcoded values
   - Tags where supported

## Validation
- Run `terraform fmt`
- Run `terraform validate`
- Check for plan errors
