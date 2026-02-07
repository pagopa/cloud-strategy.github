# Agents Catalog

This folder contains optional custom agents for focused tasks.

## Recommended routing
- Read-only: `Planner`, `Reviewer`, `SecurityReviewer`, `WorkflowSupplyChain`, `TerraformGuardrails`, `IAMLeastPrivilege`.
- Write-capable: `Implementer`.

## Selection guide
1. Use `Planner` at design stage.
2. Use `Implementer` for execution after requirements are stable.
3. Use `Reviewer` for non-security quality gates.
4. Use `TerraformGuardrails` and `IAMLeastPrivilege` on policy/infrastructure changes.
5. Use `WorkflowSupplyChain` on workflow changes.
6. Use `SecurityReviewer` as final security gate.
