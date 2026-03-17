---
name: TechAITerraform
description: Use when the user needs to add, modify, or refactor Terraform resources, variables, outputs, data sources, or modules. Covers both feature-level changes within existing configurations and creation of reusable modules.
---

# Terraform Skill

## When to use
- Add or modify resources, variables, outputs, data sources in existing configurations.
- Create a new reusable Terraform module from scratch.
- Refactor inline resources into a module.
- Decide whether a change belongs in an existing configuration or warrants a new module.

## Feature vs module — when to use which

See `references/decision-guide.md` for the full decision flowchart. Quick rule:

| Situation | Use |
|---|---|
| Adding resources to an existing root/environment config | Feature (inline) |
| Logic reused across 2+ root configs or repositories | Module |
| Complex resource group with its own lifecycle | Module |
| One-off resource for a single environment | Feature (inline) |

## Mandatory rules
- Follow `.github/instructions/terraform.instructions.md` for provider and external module pinning.
- Use `snake_case` for all Terraform identifiers.
- Add `description` and `type` to every variable.
- Avoid `default` values in variables for non-module components; pass configurations via `.tfvars`.
- Avoid using `locals` for hardcoded configuration; use direct values in the code unless they need to be configurable.
- *Note:* The above two rules on avoiding defaults and restricting locals do not apply to reusable standalone modules.
- Add `description` to every output.
- Avoid hardcoded values (IDs, ARNs, subscription IDs, secrets).
- Apply tags on all taggable resources.
- Preserve naming and folder conventions of the target repository.
- Preserve stable module input/output contracts when modifying existing modules.

## Module standard layout
- `main.tf` — resources and data sources
- `variables.tf` — input variables with `description` and `type`
- `outputs.tf` — outputs with `description`
- `versions.tf` — `required_version` and `required_providers` with pinned versions
- `README.md` — usage example, inputs, outputs

## Minimal feature example
```hcl
variable "project_id" {
  description = "Project identifier"
  type        = string
}

resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_id}-logs"

  tags = {
    Project = var.project_id
  }
}

output "logs_bucket_id" {
  description = "Logs bucket id"
  value       = aws_s3_bucket.logs.id
}
```

## Minimal module example
```hcl
# variables.tf
variable "name" {
  description = "Resource base name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "Must be one of: dev, uat, prod."
  }
}

# main.tf
resource "aws_s3_bucket" "this" {
  bucket = "${var.name}-${var.environment}"

  tags = {
    Name        = var.name
    Environment = var.environment
  }
}

# outputs.tf
output "bucket_id" {
  description = "Created bucket id"
  value       = aws_s3_bucket.this.id
}
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `count` where `for_each` with logical keys fits | Index-based addressing causes drift when items are added/removed in the middle | Use `for_each` with a map or `toset()` of logical keys |
| Missing `description` on variables and outputs | Undocumented interfaces block collaboration and code review | Always add `description` — it costs nothing |
| Hardcoded ARNs, subscription IDs, or account IDs | Breaks portability between environments and accounts | Use variables or data sources |
| Provider version not pinned in `required_providers` | Non-deterministic plans across machines and CI | Pin with `~>` or exact version constraint |
| `ignore_changes` without documented rationale | Hides drift and confuses future maintainers | Add a comment explaining why the lifecycle rule exists |
| Creating a module for a one-off resource group | Over-engineering adds indirection without reuse benefit | Keep it inline; extract when 2+ callers emerge |
| Breaking module interface (removing/renaming variables) | Breaks all consumers silently | Deprecate old vars, add new ones, migrate consumers, then remove |
| Missing `versions.tf` in modules | No reproducibility guarantee | Always include `required_version` and `required_providers` |
| Missing `prevent_destroy` on critical production resources | Accidental deletion during `terraform apply` | Add lifecycle for databases, DNS zones, encryption keys |
| `default = ""` instead of `default = null` for optional strings | Empty string passes validation but means "no value" ambiguously | Use `null` for truly optional inputs |

## Cross-references
- **TechAICloudPolicy** (`.github/skills/tech-ai-cloud-policy/SKILL.md`): for governance policies (SCP, Azure Policy, GCP Org Policy) applied alongside Terraform infra.
- **TechAICICDWorkflow** (`.github/skills/tech-ai-cicd-workflow/SKILL.md`): for CI/CD pipelines that run `terraform plan/apply`.

## Validation
- `terraform fmt -check -recursive`
- `terraform validate`
- Review `terraform plan` output for unexpected changes
- For modules: run example/consumer plan review
