# Agents Catalog

This folder contains optional custom agents for focused tasks.

## Resolution order
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply prompt and referenced skill details.

## Recommended routing
- Read-only: `TechAIPlanner`, `TechAIReviewer`, `TechAISecurityReviewer`, `TechAIWorkflowSupplyChain`, `TechAITerraformGuardrails`, `TechAIIAMLeastPrivilege`.
- PR-focused: `TechAIPRWriter`.
- Write-capable: `TechAIImplementer`.
- Repo-only standards specialists: `TechAIGlobalCustomizationBuilder`, `TechAIGlobalCustomizationAuditor`.

## Why generic core agents
- `TechAIPlanner`, `TechAIImplementer`, and `TechAIReviewer` are workflow roles, not language roles.
- Technology is resolved from file paths and prompt inputs (for example, `**/*.py` -> Python instructions).
- Avoid creating per-language triplets unless repeated failures justify a dedicated specialist.

## Selection guide
1. Use `TechAIPlanner` at design stage.
2. Use `TechAIImplementer` for execution after requirements are stable.
3. Use `TechAIReviewer` for non-security quality gates.
4. Use `TechAITerraformGuardrails` and `TechAIIAMLeastPrivilege` on policy/infrastructure changes.
5. Use `TechAIWorkflowSupplyChain` on workflow changes.
6. Use `TechAIPRWriter` to create or update PR title/body from template and diff.
7. Use `TechAISecurityReviewer` as final security gate.
8. Use `TechAIGlobalCustomizationBuilder` for GitHub Copilot customization assets in this standards repository.
9. Use `TechAIGlobalCustomizationAuditor` as the final gate for those customization changes.
