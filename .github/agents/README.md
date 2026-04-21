# Agents Catalog

This folder contains deliberate custom agents for repository-owned direct-owner operations plus repo-only sync workflows.

## Resolution order

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply referenced skill details.

## Recommended owner selection

- Safe fallback when the right operational lane is still ambiguous: `internal-planning-leader`.
- Direct canonical owners: `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, `internal-critical-master`.
- Source-side catalog sync, rationalization, overlap cleanup, and governance drift correction in this repository: `internal-sync-external-resources`.
- Cross-repository baseline propagation: `internal-sync-global-copilot-configs-into-repo`.
- PR-focused work should use the `internal-pr-editor` skill because this repository does not currently ship a dedicated PR editor agent.

## Repo-only agents (not synced to consumers)

- `internal-sync-external-resources`
- `internal-sync-global-copilot-configs-into-repo`

## Why this catalog stays deliberate

- This repository keeps a deliberate set of source-side command-center agents under `.github/agents/`.
- Prefer one cohesive agent per recurring operational or governance workflow.
- Keep the four canonical owners explicit and non-overlapping, and keep reusable logic in skills instead of bloating agent bodies.
- Keep the direct-entry model explicit; canonical owners define boundaries and recommend a better owner instead of handing off automatically.
- Technology is resolved from file paths and prompt inputs (for example, `**/*.py` -> Python instructions).
- Prefer skills for detailed task procedures unless a dedicated agent file is present.

## Selection guide

1. Use `internal-planning-leader` when the user has not yet chosen the right owner or the request could plausibly be execution, planning, review, or challenge.
2. Use `internal-delivery-operator` for clear, local execution work with concrete verification and no non-trivial strategic tradeoffs.
3. Use `internal-review-guard` for defect-first review, merge readiness, regression analysis, and evidence-based validation.
4. Use `internal-critical-master` for pre-mortems, objection-first pressure tests, lateral reframing, and failure-mode analysis.
5. Use `internal-sync-external-resources` when governing the live `.github/` catalog in this repository: refresh approved external assets, align naming, consolidate overlap, retire obsolete entries, and clean up downstream governance references. Unless the user explicitly asks for an audit or plan first, treat `sync` as a full apply request.
6. Use `internal-sync-global-copilot-configs-into-repo` when aligning a consumer repository with the managed Copilot baseline from this standards repository.
7. Use skills from `.github/skills/` for work that does not need a dedicated agent file.
