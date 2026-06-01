---
name: internal-makefile
description: Use when editing Makefile or .mk files that need deterministic targets, readable recipes, and phony target hygiene.
---

# Internal Makefile

## Referenced skills

- None.

## When to use

- `Makefile` or `*.mk` changes.
- Reviews of target naming, phony declarations, recipe clarity, and deterministic command behavior.
- Small build-orchestration edits that do not belong to a narrower runtime or CI owner.

## When not to use

- CI workflow semantics are the main concern; use the matching CI owner.
- The Make target only wraps a script whose behavior is owned by a language or script skill.
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
- Use `make -n <target>` when execution would mutate state.
- Run the nearest focused test when a target is part of validator behavior.
