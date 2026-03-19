# Agents Catalog

This folder contains optional custom agents for focused tasks.

## Resolution order
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply prompt and referenced skill details.

## Recommended routing
- Read-only: `TechAIPlanner`, `TechAIReviewer`, `TechAISecurityReviewer`, `TechAIWorkflowSupplyChain`, `TechAITerraformGuardrails`, `TechAIIAMLeastPrivilege`.
- Analysis-to-plan: `TechAIPairArchitectAnalysisExecutor` (takes `TechAIPairArchitect` output, re-evaluates, produces execution plan).
- PR-focused: `TechAIPREditor`.
- Write-capable: `TechAIImplementer`.

## Repo-only agents (not synced to consumers)
- `TechAISyncGlobalCopilotConfigsIntoRepo`

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
6. Use `TechAIPREditor` to create or update PR title/body from template and diff.
7. Use `TechAISecurityReviewer` as final security gate.
8. Use `TechAISyncGlobalCopilotConfigsIntoRepo` to align a consumer baseline before creating repo-owned internal assets.
9. Use `TechAIPairArchitectAnalysisExecutor` after `TechAIPairArchitect` to re-evaluate findings, produce a validated execution plan with per-finding decision tables, extract lessons learned, and prepare work packages for `TechAIImplementer`.
