---
name: internal-makefile
description: Use when editing or reviewing Makefile or .mk syntax, targets, prerequisites, recipes, variables, or static format checks.
---

# Internal Makefile

## When to use

- Makefile or `.mk` edits where static Make format ownership is the active
  concern.
- Reviews of targets, prerequisites, recipe prefixes, `.PHONY`, variables,
  and `$` versus `$$`.
- Reviews of safe static validation and routing when embedded shell behavior
  dominates.

## When not to use

- Embedded shell behavior dominates the recipe; use `/internal-bash`.
- CI or runtime semantics are the main concern; use the matching owner.
- Generated Makefiles unless the generator is the intended edit point.

## Baseline

- Mark non-file targets with `.PHONY`.
- Keep prerequisites, order-only prerequisites, variables, and recipes
  explicit and readable.
- Preserve tab-prefixed recipes and distinguish Make variables (`$`) from
  shell variables (`$$`).
- Treat recursive Make, parallelism, recipe side effects, and domain behavior
  as review concerns.
- `make` and `make -n` are not generic safety boundaries; `make -n` is only a
  preview, so inspect recipes before execution.

## Validation

Run the bundle-owned static checker with explicit files:

```bash
.github/skills/internal-makefile/scripts/check.sh FILE [FILE ...]
```

The checker returns `0` when checks passed within supported scope, `1` for
format findings, and `2` for usage, dependency, file, or internal failures.
It requires `checkmake` 0.3.2 and never invokes GNU Make or recipe commands.
Supported checks are parser-backed Makefile rules and configured static
limits. Variable intent, `$`/`$$` behavior, parallelism, order-only
prerequisites, recipe side effects, and domain behavior are unsupported.
