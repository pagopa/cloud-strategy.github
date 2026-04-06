# AGENTS.md - Copilot bridge

This file is the repository-root bridge for GitHub Copilot customization resources.

## Bridge contract

1. Always load `.github/copilot-instructions.md` first. It is the primary detailed policy file for this repository.
2. Use `.github/INVENTORY.md` for the exact live path inventory.
3. Use the live Copilot resources under `.github/` only when they are relevant to the current task:
   - `.github/instructions/` for `applyTo`-driven file guidance
   - `.github/prompts/` for repeatable task entry points when prompt files are present
   - `.github/skills/` for reusable workflows and implementation patterns
   - `.github/agents/` for routeable operating roles

## Naming contract

- Repository-owned resources created in `cloud-strategy.github` use the `internal-*` prefix.
- Repository-owned resources created in other repositories use the `local-*` prefix.
- Imported upstream resources keep the `<short-repo>-<original-resource-name>` form.

## Bridge rule

- Keep detailed policy, validation, workflow, and governance guidance in `.github/copilot-instructions.md`.
- Keep this file limited to bridge-level loading, naming, and discovery.
- Do not duplicate detailed policy or exact inventory here.
