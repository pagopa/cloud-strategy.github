# Agents Catalog

This folder contains optional custom agents for focused tasks.

## Resolution order
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply prompt and referenced skill details.

## Recommended routing
- Full sync of approved upstream skills and instructions, plus catalog rationalization, overlap cleanup, and drift analysis when explicitly requested: `internal-agent-sync`.
- Cross-repository baseline propagation: `internal-sync-global-copilot-configs-into-repo`.
- PR-focused work should use the `internal-pr-editor` prompt and skill because this repository does not currently ship a dedicated PR editor agent.

## Repo-only agents (not synced to consumers)
- `internal-agent-sync`
- `internal-sync-global-copilot-configs-into-repo`

## Why this catalog is small
- This repository keeps a small set of source-side command-center agents under `.github/agents/`.
- Technology is resolved from file paths and prompt inputs (for example, `**/*.py` -> Python instructions).
- Prefer prompts and skills for delivery, planning, and review flows unless a dedicated agent file is present.

## Selection guide
1. Use `internal-agent-sync` when importing, installing, refreshing, renaming, consolidating, retiring, or auditing approved upstream skills and instructions. Unless the user explicitly asks for an audit or plan first, treat `sync` as a full apply request.
2. Use `internal-sync-global-copilot-configs-into-repo` when aligning a consumer repository with the managed Copilot baseline from this standards repository.
3. Use prompts and skills from `.github/prompts/` and `.github/skills/` for planning, editing, review, and implementation work that does not have a dedicated agent file.
