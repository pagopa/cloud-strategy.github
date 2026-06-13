---
name: agent-os-index-standards
description: Portable workflow for rebuilding agent-os/standards/index.yml from standards files with deterministic ordering and short descriptions.
---

# Agent OS Index Standards

## Referenced skills

- None.

## When to use

- `agent-os/standards/index.yml` is stale, missing entries, or includes deleted files.
- Standards files were recently added, renamed, or removed.

## When not to use

- You need to discover new standards from code; use `agent-os-discover-standards`.
- You need to inject standards into a conversation or plan; use `agent-os-inject-standards`.

## Workflow

1. Scan `agent-os/standards/` recursively for `.md` files.
2. Interpret files in `agent-os/standards/` root as the reserved folder key `root`.
3. Load the current `agent-os/standards/index.yml` when present.
4. For each new file, propose a one-sentence description and confirm it before writing.
5. Remove stale index entries for deleted files automatically.
6. Write YAML sorted by folder name and then file name.
7. Report what changed: entries added, removed, and unchanged.

## Boundaries

- Keep descriptions to one short sentence.
- Use filenames without `.md` extension in index keys.
- Do not create a physical `root/` folder.

## Validation

- Every standard file has an index entry.
- No index entry points to a missing file.
- Ordering is deterministic (alphabetical folders, alphabetical file keys).

## Source command parity

- Derived from `.claude/commands/agent-os/index-standards.md`.
- Runtime language is portable for Copilot and Codex and does not rely on Claude slash commands.
