---
name: internal-markdown
description: Use when editing or reviewing repository-owned Markdown that needs concise structure, explicit paths, links, and maintainable prose.
---

# Internal Markdown

## Referenced skills

- None.

## When to use

- Repository-owned Markdown documentation, prompts, skills, agents, plans, and governance prose.
- Reviews focused on heading hierarchy, concise sections, path formatting, local links, and stale examples.
- Markdown edits without a narrower owner such as retained-plan, skill-authoring, or agent-authoring rules.

## When not to use

- Deep skill-reference rewrites that change bundle boundaries; use the skill-authoring owner first.
- Imported upstream Markdown that must remain verbatim unless the task explicitly allows a fork or refresh.

## Baseline

- Use Plain Technical English for repository-owned prose.
- Prefer task-oriented sections and concise bullets over long narrative blocks.
- Use backticks for commands, paths, identifiers, schema fields, and literal values.
- Keep links explicit and maintainable.
- Preserve required technical names unchanged.
- Update docs when behavior or workflow contracts change.

## Validation

- Run the closest Markdown lint or repository documentation check when available.
- Re-check local links when moving or deleting Markdown assets.
- For generated documentation, run the generator instead of editing output by hand.
