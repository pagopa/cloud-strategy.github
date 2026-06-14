---
description: Terraform authoring standards for readability, typed interfaces, and validation-first delivery.
applyTo: "**/*.tf"
excludeAgent: "cloud-agent"
---

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

# Terraform Review Checks

- Verify variable and output types are explicit and match actual usage.
- Flag provider, module, or version constraints that are missing or too loose.
- Check resource changes for destructive replacement or drift-risk behavior.
- Verify IAM and network changes follow least-privilege intent.
- Report hidden dependencies that rely on implicit ordering.
- Check naming, tagging, and state-sensitive references for consistency.
- Flag missing validation or precondition logic on critical inputs.
