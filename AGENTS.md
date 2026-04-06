# AGENTS.md - customization-standards

This file is the repository-root bridge for GitHub Copilot customization resources.

`.github/copilot-instructions.md` is the primary detailed policy file.
Update `.github/copilot-instructions.md` first when policy, validation, or workflow guidance changes, then refresh root `AGENTS.md` only for routing, naming, discovery, or inventory alignment.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal or alternative assistant runtimes in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- External resources must use `<short-repo>-<original-resource-name>` in filenames and `name:` values.
- Resources created locally in `cloud-strategy.github` must use the `internal-` prefix in filenames and `name:` values.
- Resources created locally in other repositories must use the `local-` prefix in filenames and `name:` values.
- Root `AGENTS.md` is the canonical project-owned bridge file.
- Do not keep legacy aliases, fallback copies, or deprecated variants. Preserve an alias only when an active backward-compatibility requirement is explicitly documented.

## Imported Resource Policy

- Treat every non-`internal-*` resource in this repository as an imported upstream asset that should remain verbatim unless the user explicitly asks to refresh, replace, or fork that import.
- Express repository-specific behavior through `internal-*` resources only.
- Use `internal-*` resources as wrappers, extensions, adapters, or routing layers that map imported upstream resources to this repository's local needs.

## Layered Routing Model

- `obra-*` skills are the strategic lane for framing, planning, simplification, tradeoff handling, and verification.
- `internal-*` skills are the tactical lane and the default repository-owned execution or governance owners.
- Imported non-`internal-*` skills remain support-only unless no internal owner exists for the capability.

## Decision Priority

1. Apply `.github/copilot-instructions.md` as the primary detailed policy layer.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior.
4. Apply matching `.github/instructions/*.instructions.md` using `applyTo`.
5. Apply selected `.github/prompts/*.prompt.md`.
6. Apply implementation details from referenced `.github/skills/*/SKILL.md`.
7. Use `.github/INVENTORY.md` for exact path discovery only; do not duplicate detailed policy in this file.

## Agent Routing

- `internal-router`: recommended operational front door when the correct owner is not obvious yet.
- Only `internal-router` actively delegates between canonical owners. The four canonical owners stay boundary-driven and recommend a better owner when the request no longer fits.
- `internal-fast-executor`: clear, local, execution-owned work with concrete verification.
- `internal-planning-leader`: ambiguity resolution, non-trivial repository-owned authoring, and strategy or rollout decisions.
- `internal-review-guard`: defect-first review, merge readiness, regression risk, and evidence-based validation.
- `internal-critical-challenger`: pre-mortems, reasoning stress tests, and failure-mode analysis.
- `internal-sync-control-center`: source-side governance of the live `.github/` Copilot catalog in this repository.
- `internal-sync-global-copilot-configs-into-repo`: cross-repository Copilot-core alignment and redundancy audits.
- `internal-pr-editor` is intentionally prompt-routed; use the `internal-pr-editor` prompt with the `internal-pr-editor` skill for pull request body generation.
- `internal-data-registry` remains installed as intentionally dormant tactical capacity until a dedicated routing owner is added.
- Imported `awesome-*` agents and repo-only `internal-sync-*` agents stay outside the canonical operational ownership model.
- Do not reference agents that are not present in `.github/agents/`.

## Repository Defaults

- Primary focus: reusable, repository-agnostic GitHub Copilot customization standards.
- Profile hint: `minimal`
- Keep root `AGENTS.md` light: naming, routing, discovery, and the pointer to exact path inventory only.
- Keep detailed behavior, validation, PR or workflow policy, and implementation guardrails in `.github/copilot-instructions.md`.
- Completion-report details live in `.github/copilot-instructions.md`; keep only the bridge-level pointer here.
- Exact path inventory lives in `.github/INVENTORY.md`; keep only the bridge pointer here.
- Prioritize these paths:
  - `.github/instructions`
  - `.github/prompts`
  - `.github/skills`
  - `.github/agents`
  - `.github/scripts`

## Inventory

- Exact path inventory lives in `.github/INVENTORY.md`.
- Keep only the bridge pointer here so `AGENTS.md` stays lightweight.
