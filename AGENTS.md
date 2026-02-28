# AGENTS.md - cloud-strategy.github

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy
- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.

## Decision Priority
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior (agent-first routing).
4. Apply matching files under `instructions/*.instructions.md` using `applyTo`.
5. Apply selected prompt constraints from `prompts/*.prompt.md`.
6. Apply implementation details from referenced `skills/*/SKILL.md`.
7. If no agent is explicitly selected, default to `Implementer`.

## Stack Resolution Rules
- The agent role is behavioral, not language-specific.
- Resolve stack from target files and explicit prompt inputs.
- Use matching `applyTo` rules:
  - `**/*.py` -> `instructions/python.instructions.md`
  - `**/*.java` -> `instructions/java.instructions.md`
  - `**/*.sh` -> `instructions/bash.instructions.md`
  - `**/workflows/**` -> `instructions/github-actions.instructions.md`
  - `**/actions/**/action.y*ml` -> `instructions/github-action-composite.instructions.md`
- If a change spans multiple stacks, apply all relevant instruction files.

## Agent Routing
- Use `Planner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `Implementer` for direct code/config changes and validations.
- Use `Reviewer` for quality gates and defect/regression findings.
- Use specialist agents (`WorkflowSupplyChain`, `SecurityReviewer`, `TerraformGuardrails`, `IAMLeastPrivilege`, `PRWriter`) only when their domain matches the task.

## PR and Workflow Conventions
- PR content must follow `pull_request_template.md` in exact section order.
- For GitHub Actions pinning, each full SHA must include an adjacent comment with release/tag reference.
