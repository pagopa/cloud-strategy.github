---
description: Create or modify reusable Terraform modules and components with portable conventions
name: internal-terraform-module
agent: agent
argument-hint: action=<create|modify> module_name=<name> change_type=<resource|variable|output|data_source|module> purpose=<purpose> [target_path=<path>]
---

# Terraform Module

## Context
Use this prompt to create or modify Terraform modules/components while keeping the implementation generic and reusable.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Module name**: ${input:module_name}
- **Change type**: ${input:change_type:resource,variable,output,data_source,module}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:infra/terraform}

## Instructions
1. Use `.github/skills/internal-terraform/SKILL.md` and `.github/instructions/internal-terraform.instructions.md`.
2. Keep variable names, outputs, and descriptions domain-neutral.
3. Avoid hardcoded tenant/account/subscription/project identifiers.
4. Document assumptions and provider requirements explicitly.
5. Keep module interfaces stable unless a breaking change is requested.
6. Follow `.github/instructions/internal-terraform.instructions.md` for provider and external module pinning.

## Minimal example
- Input: `action=create module_name=storage_baseline change_type=module purpose="Provide portable object-storage baseline" target_path=infra/terraform/modules`
- Expected output:
  - New module with explicit variables, outputs, and provider-agnostic naming.
  - Clear documentation comments for non-obvious logic.

## Validation
- Run `terraform fmt` on changed files.
- Run `terraform validate` in the affected module/root.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
