# Agents Catalog

This folder contains deliberate custom agents for repository-owned operational routing plus repo-only sync workflows.

## Resolution order
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply referenced skill details.

## Recommended routing
- Default operational front door: `internal-router` (routes only; it does not edit files or implement changes).
- Direct canonical owners: `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, `internal-critical-challenger`.
- Source-side catalog sync, rationalization, overlap cleanup, and governance drift correction in this repository: `internal-sync-control-center`.
- Cross-repository baseline propagation: `internal-sync-global-copilot-configs-into-repo`.
- PR-focused work should use the `internal-pr-editor` skill because this repository does not currently ship a dedicated PR editor agent.

## Repo-only agents (not synced to consumers)
- `internal-sync-control-center`
- `internal-sync-global-copilot-configs-into-repo`

## Why this catalog stays deliberate
- This repository keeps a deliberate set of source-side command-center agents under `.github/agents/`.
- Prefer one cohesive agent per recurring operational or governance workflow.
- Keep the operational front door explicit, keep the four canonical owners non-overlapping, and keep reusable logic in skills instead of bloating agent bodies.
- Keep downstream owner selection in `internal-router` only; canonical owners define boundaries and recommend a better owner instead of handing off automatically unless a scoped contract explicitly allows invoking `internal-router` as a second parallel lane.
- Technology is resolved from file paths and prompt inputs (for example, `**/*.py` -> Python instructions).
- Prefer skills for detailed task procedures unless a dedicated agent file is present.

## Selection guide
1. Use `internal-router` when the user has not yet chosen the right owner or the request could plausibly be execution, planning, review, or challenge. Treat it as dispatch-only.
2. Use `internal-fast-executor` for clear, local execution work with concrete verification and no non-trivial strategic tradeoffs.
3. Use `internal-planning-leader` for ambiguity resolution, non-trivial repository-owned authoring, design decisions, and rollout or governance planning.
4. Use `internal-review-guard` for defect-first review, merge readiness, regression analysis, and evidence-based validation.
5. Use `internal-critical-challenger` for pre-mortems, objection-first pressure tests, lateral reframing, and failure-mode analysis.
6. Use `internal-sync-control-center` when governing the live `.github/` catalog in this repository: refresh approved external assets, align naming, consolidate overlap, retire obsolete entries, and clean up downstream governance references. Unless the user explicitly asks for an audit or plan first, treat `sync` as a full apply request.
7. Use `internal-sync-global-copilot-configs-into-repo` when aligning a consumer repository with the managed Copilot baseline from this standards repository.
8. Use skills from `.github/skills/` for work that does not need a dedicated agent file.
