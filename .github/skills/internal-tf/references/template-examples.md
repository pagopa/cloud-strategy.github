# Terraform Template Examples

## Minimal feature

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
  description = "Created logs bucket identifier"
  value       = aws_s3_bucket.logs.id
}
```

## Minimal typed module interface

```hcl
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

output "resource_name" {
  description = "Stable name exposed by the module"
  value       = "${var.name}-${var.environment}"
}
```

Use the router for module architecture, provider behavior, state, and delivery decisions beyond this language-level interface.
