# Agents Catalog

This folder contains optional custom agents for focused tasks.

## Recommended routing
- `Planner`: analysis and implementation plans (read-only).
- `Implementer`: execute code and config changes end-to-end.
- `Reviewer`: structured quality/code review findings.
- `SecurityReviewer`: security-focused review before merge.
- `WorkflowSupplyChain`: GitHub Actions and CI/CD supply-chain checks.
- `TerraformGuardrails`: Terraform guardrails and lifecycle safety review.
- `IAMLeastPrivilege`: IAM/policy least-privilege review.

## Selection guide
1. Use `Planner` at design stage.
2. Use `Implementer` for execution after requirements are stable.
3. Use `Reviewer` for non-security quality gates.
4. Use `TerraformGuardrails` and `IAMLeastPrivilege` on policy/infrastructure changes.
5. Use `WorkflowSupplyChain` on workflow changes.
6. Use `SecurityReviewer` as final security gate.
