---
name: TechAITerraformFeature
description: Add or modify Terraform resources, variables, outputs, and data sources within existing configurations. Use when the user needs to add cloud resources, modify infrastructure, create variables or outputs, update existing .tf files, or make feature-level Terraform changes that do not require a new reusable module.
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
- Follow `.github/instructions/terraform.instructions.md` for provider and external module pinning.

## Minimal example
```hcl
variable "project_id" {
  description = "Project identifier"
  type        = string
}

resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_id}-logs"
}

output "logs_bucket_id" {
  description = "Logs bucket id"
  value       = aws_s3_bucket.logs.id
}
```

## Validation
- `terraform fmt`
- `terraform validate`
- Review `terraform plan`
