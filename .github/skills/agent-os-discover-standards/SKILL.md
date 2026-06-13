---
name: agent-os-discover-standards
description: Portable workflow for discovering concise project standards and writing them to agent-os/standards/ for Copilot and Codex sessions without Claude slash-command dependencies.
---

# Agent OS Discover Standards

## Referenced skills

- `agent-os-index-standards`: on-demand refresh of `agent-os/standards/index.yml` after standard files are added or removed.

## When to use

- You need to discover tribal conventions from code and store them as reusable standards.
- The target output is one or more files under `agent-os/standards/`.
- You want a Copilot/Codex-friendly flow with explicit user confirmations.

## When not to use

- You only need to rebuild the index; use `agent-os-index-standards`.
- You are implementing code changes rather than documenting standards.
- You need to execute standards, not author or refine them.

## Workflow

1. Propose a focused area to inspect (or confirm the area provided by the user).
2. Review representative files and extract only non-obvious, repeated, opinionated patterns.
3. For each candidate standard, ask 1-2 short why/exceptions questions before drafting.
4. Draft one concise standard at a time and request explicit approval before writing.
5. Write approved files to `agent-os/standards/<folder>/<name>.md`.
6. Refresh the index with `agent-os-index-standards` when file changes are complete.

## Boundaries

- Keep standards concise and scannable for AI context windows.
- Do not copy framework defaults unless they are project-specific constraints.
- Do not write files without user confirmation.

## Validation

- New standards are located under `agent-os/standards/`.
- Each standard contains one concept with concrete examples when useful.
- `agent-os/standards/index.yml` is updated after additions or deletions.

## Source command parity

- Derived from `.claude/commands/agent-os/discover-standards.md`.
- Runtime language is portable for Copilot and Codex and does not rely on Claude slash commands.
