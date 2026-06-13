---
name: agent-os-plan-product
description: Portable workflow for creating or updating agent-os/product mission, roadmap, and tech-stack documents through lightweight guided questions.
---

# Agent OS Plan Product

## Referenced skills

- `agent-os-inject-standards`: on-demand lookup of relevant standards, including `agent-os/standards/global/tech-stack.md` when present.

## When to use

- Product context docs are missing or outdated in `agent-os/product/`.
- You need a lightweight mission, roadmap, and tech-stack baseline for later planning.

## When not to use

- You are shaping a concrete feature spec; use `agent-os-shape-spec`.
- You only need one small edit in product docs without guided discovery.

## Workflow

1. Check which files already exist: `mission.md`, `roadmap.md`, `tech-stack.md`.
2. If files exist, ask whether to replace all, update selected files, or cancel.
3. Collect concise inputs for product problem, target users, and differentiator.
4. Collect MVP and post-launch feature priorities.
5. Reuse `agent-os/standards/global/tech-stack.md` when applicable, otherwise collect stack details.
6. Write or update files under `agent-os/product/` with clear sections.

## Boundaries

- Do not overwrite existing docs without explicit user confirmation.
- Keep content concise and editable.
- If answers are incomplete, use clear placeholders instead of inventing detail.

## Validation

- Target files exist under `agent-os/product/` after approval.
- Content reflects user-provided inputs and selected update mode.
- Tech stack section clearly distinguishes frontend, backend, database, and other tools when relevant.

## Source command parity

- Derived from `.claude/commands/agent-os/plan-product.md`.
- Runtime language is portable for Copilot and Codex and does not rely on Claude slash commands.
