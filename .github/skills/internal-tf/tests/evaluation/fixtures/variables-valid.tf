variable "environment" {
  type        = string
  description = "Deployment environment."

  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "Must be one of: dev, uat, prod."
  }
}

output "environment" {
  description = "Selected deployment environment."
  value       = var.environment
}
