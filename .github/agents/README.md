# Agents Catalog

This folder contains optional custom agents for deliberate command-center tasks.

## Resolution order
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply prompt and referenced skill details.

## Recommended routing
- Source-side catalog sync, rationalization, overlap cleanup, and governance drift correction in this repository: `internal-sync-control-center`.
- Cross-repository baseline propagation: `internal-sync-global-copilot-configs-into-repo`.
- PR-focused work should use the `internal-pr-editor` prompt and skill because this repository does not currently ship a dedicated PR editor agent.

## Repo-only agents (not synced to consumers)
- `internal-sync-control-center`
- `internal-sync-global-copilot-configs-into-repo`

## Why this catalog stays deliberate
- This repository keeps a deliberate set of source-side command-center agents under `.github/agents/`.
- Prefer one cohesive agent per recurring command-center workflow. A broader agent is acceptable when its skills reinforce the same operating role.
- Split agents when routing becomes ambiguous or the file mixes disjoint responsibilities. Do not split purely to minimize file size or token count.
- Technology is resolved from file paths and prompt inputs (for example, `**/*.py` -> Python instructions).
- Prefer prompts and skills for detailed task procedures unless a dedicated agent file is present.

## Selection guide
1. Use `internal-sync-control-center` when governing the live `.github/` catalog in this repository: refresh installed approved external assets, align naming, consolidate overlap, retire obsolete entries, and clean up downstream governance references. Unless the user explicitly asks for an audit or plan first, treat `sync` as a full apply request.
2. Use `internal-sync-global-copilot-configs-into-repo` when aligning a consumer repository with the managed Copilot baseline from this standards repository.
3. Use prompts and skills from `.github/prompts/` and `.github/skills/` for planning, editing, review, and implementation work that does not have a dedicated agent file.
