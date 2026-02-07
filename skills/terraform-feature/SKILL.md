---
name: terraform-feature
description: Add or modify Terraform resources, variables, outputs, and data sources.
---

# Terraform Feature Skill

## When to use
- Adding new resources.
- Modifying existing resources.
- Introducing variables and outputs.
- Creating data sources.

## Discovery steps

1. Inspect existing files in the target directory.
2. Identify naming conventions and patterns to preserve.
3. Check related resources that may require updates.
4. Reuse existing variables whenever possible.

## Resource example

```hcl
resource "aws_iam_role" "example" {
  name        = "pagopa-${var.environment}-example"
  description = "Role for example purpose"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}
```

## Variable example

```hcl
variable "example_config" {
  description = "Configuration for example resource"
  type = object({
    enabled = bool
    name    = string
  })
  default = {
    enabled = false
    name    = ""
  }
}
```

## Output example

```hcl
output "example_arn" {
  description = "ARN of the example resource"
  value       = aws_iam_role.example.arn
}
```

## Checklist
- [ ] Naming follows repository conventions.
- [ ] Variables include `description` and `type`.
- [ ] Outputs include `description`.
- [ ] No hardcoded values.
- [ ] Tags are applied where supported.
- [ ] `terraform fmt` and `terraform validate` pass.
