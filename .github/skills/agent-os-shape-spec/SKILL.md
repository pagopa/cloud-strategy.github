---
name: agent-os-shape-spec
description: Portable workflow for shaping significant work into agent-os/specs/<timestamp-slug>/ with clear scope, references, standards, and execution-ready tasks.
---

# Agent OS Shape Spec

## Referenced skills

- `agent-os-inject-standards`: on-demand discovery and inclusion of relevant standards during shaping.
- `agent-os-plan-product`: on-demand product-context refresh when `agent-os/product/` context is missing or stale.

## When to use

- Significant work needs explicit shaping before implementation.
- You need to save reusable planning artifacts under `agent-os/specs/`.

## When not to use

- The request is a small direct edit with clear validation.
- You are not in a planning context and no spec package is needed.

## Workflow

1. Confirm planning context and feature scope with short clarification questions.
2. Collect optional visuals and reference implementations.
3. Read product context from `agent-os/product/` when available.
4. Identify relevant standards from `agent-os/standards/index.yml` and confirm inclusion.
5. Create `agent-os/specs/YYYY-MM-DD-HHMM-<slug>/`.
6. Build an execution plan where Task 1 is always saving spec documentation.
7. Prepare `plan.md`, `shape.md`, `standards.md`, `references.md`, and `visuals/` as applicable.

## Boundaries

- Use explicit user approval language; do not rely on Claude-only plan-mode mechanics.
- Keep shaping lightweight and actionable.
- Do not auto-start implementation from shaping output without approval.

## Validation

- Spec folder uses `YYYY-MM-DD-HHMM-<slug>` naming under `agent-os/specs/`.
- Task 1 in `plan.md` is "Save spec documentation".
- Supporting files capture scope, decisions, standards, and references relevant to the work.

## Source command parity

- Derived from `.claude/commands/agent-os/shape-spec.md`.
- Runtime language is portable for Copilot and Codex and does not rely on Claude slash commands.
