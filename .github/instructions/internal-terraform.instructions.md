---
description: Terraform review checks for typed interfaces, version constraints, destructive changes, least privilege, and state-address moves.
applyTo: "**/*.tf"
excludeAgent: "cloud-agent"
---

# Terraform Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag variables missing `type` or `description`, and outputs missing `description`.
- Flag outputs that expose secrets without `sensitive = true`.
- Flag provider, module, or Terraform version constraints that are missing or too loose.
- Flag resource changes that force replacement of stateful resources, such as a changed name, identifier, or immutable argument.
- Flag renamed resources or modules without a `moved` block, and `removed` or `import` blocks without a migration note in the pull request.
- Verify IAM and network changes follow least-privilege intent.
- Report hidden dependencies that rely on implicit ordering.
- Flag hardcoded IDs, ARNs, subscription IDs, or secrets.
- Flag taggable resources without tags unless provider `default_tags` or a tagging module covers them.
- Flag non-`snake_case` Terraform identifiers.
- Flag missing `validation`, `precondition`, or `postcondition` logic on critical inputs.
