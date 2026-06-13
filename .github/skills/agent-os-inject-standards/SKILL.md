---
name: agent-os-inject-standards
description: Portable workflow for selecting and injecting relevant standards from agent-os/standards/ into implementation, skill-authoring, or planning contexts.
---

# Agent OS Inject Standards

## Referenced skills

- `agent-os-index-standards`: on-demand repair when `agent-os/standards/index.yml` is missing or stale.

## When to use

- You need standards context for code work, planning, or skill authoring.
- You want automatic suggestions from `agent-os/standards/index.yml`.
- You need explicit injection of chosen folders or files.

## When not to use

- You need to create new standards from source code; use `agent-os-discover-standards`.
- You need only to refresh index metadata; use `agent-os-index-standards`.

## Workflow

1. Determine scenario: conversation, skill authoring, or planning.
2. In auto mode, read `agent-os/standards/index.yml` and propose 2-5 relevant standards.
3. In explicit mode, resolve folder/file targets directly.
4. Confirm what to include, then inject either file references or full content.
5. If index is missing or empty, stop and request indexing via `agent-os-index-standards`.

## Boundaries

- Do not auto-load unrelated standards.
- Ask for confirmation when scenario is ambiguous.
- Keep output focused and lightweight.

## Validation

- Injected standards exist on disk under `agent-os/standards/`.
- Scenario-specific format is respected (conversation vs. skill vs. plan).
- Suggestions remain narrow and relevant to the active task.

## Source command parity

- Derived from `.claude/commands/agent-os/inject-standards.md`.
- Runtime language is portable for Copilot and Codex and does not rely on Claude slash commands.
