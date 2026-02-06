---
name: terraform-feature
description: Add or modify Terraform resources, variables, outputs, and data sources. Use for infrastructure changes and new features.
---

# Terraform Feature Skill

## When to Use
- Adding new resources to existing configuration
- Modifying existing resources
- Adding variables or outputs
- Creating data sources

## Discovery Steps

1. Check existing files in the target directory
2. Identify naming patterns and conventions
3. Look for related resources that might need updates
4. Check for existing variables that can be reused

## Adding a Resource

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

## Adding a Variable

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

## Adding an Output

```hcl
output "example_arn" {
  description = "ARN of the example resource"
  value       = aws_iam_role.example.arn
}
```

## Checklist
- [ ] Resource follows naming convention
- [ ] Variables have descriptions and types
- [ ] Outputs have descriptions
- [ ] No hardcoded values (use variables/locals)
- [ ] Tags applied where supported
- [ ] `terraform fmt` passes
