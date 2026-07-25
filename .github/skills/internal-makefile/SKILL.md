---
name: internal-makefile
description: Use when editing or reviewing Makefile or .mk files that need deterministic targets, readable recipes, and phony target hygiene.
---

# Internal Makefile

## Referenced skills

- `internal-bash`: embedded shell safety when quoting, pipelines, failure behavior, temporary files, or dynamic commands dominate a recipe change.

## When to use

- `Makefile` or `*.mk` changes.
- Reviews of target naming, phony declarations, recipe clarity, and deterministic command behavior.
- Small build-orchestration edits that do not belong to a narrower runtime or CI owner.

## When not to use

- CI workflow semantics are the main concern; use the matching CI owner.
- The Make target only wraps a script whose behavior is owned by a language or script skill.
- Embedded shell behavior dominates the recipe change; use `/internal-bash`.
- Generated Makefiles unless the generator is the intended edit point.

## Baseline

- Use lowercase, hyphenated target names.
- Mark non-file targets with `.PHONY`.
- Keep common variables near the top.
- Prefer a `help` target when the Makefile is operator-facing.
- Keep recipes readable and deterministic.
- Avoid hidden side effects in the default target.

## Validation

- Run the touched target when it is safe and deterministic.
- Treat `make -n <target>` as a preview, not a safety boundary. Recursive `$(MAKE)` recipes and forced recipe lines may execute and produce side effects, so inspect the recipe first.
- Run the nearest focused test when a target is part of validator behavior.
