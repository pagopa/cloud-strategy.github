---
name: internal-bash-script
description: Use when creating, reviewing, or modifying standalone Bash or POSIX `sh` scripts, utilities, wrappers, launchers, or other operator-facing shell entrypoints. Route embedded shell fragments and sourced helpers inside another program to /internal-bash.
---

# Internal Bash Script

## When to use

- New Bash scripts.
- Existing Bash scripts that need review or updates.
- Standalone operator-facing wrappers, launchers, and shell utilities.

## When not to use

- Embedded shell fragments and sourced helpers inside another program; route
  them to `/internal-bash`.
- Sourced or non-operator Bash helpers that do not own an operator-facing
  entrypoint.
- Workflow or platform behavior beyond the standalone shell entrypoint.

## Dialect decision

Classify the shell before choosing script patterns. Preserve the declared
interpreter and record the execution environment and compatibility target:

- `Dialect: Bash` when the entrypoint and runtime provide Bash.
- `Dialect: POSIX`sh`` when the entrypoint or deployment target requires POSIX
  shell syntax.

Require an explicit POSIX baseline before treating POSIX.1-2024 Issue 8
behavior as portable. Bash invoked as `sh` is not cross-shell portability proof,
and the interpreter must not be changed silently.

## Portable core

Quote expansions, check statuses at correctness boundaries, use `if`, `case`,
`test`, or `[ ]` for shared control flow, validate dependencies before first
use, and use `mktemp` with cleanup traps for temporary state.

## Bash branch

For `Dialect: Bash`, follow the deployment shebang convention, normally
`#!/usr/bin/env bash`, and use `set -euo pipefail` with documented exceptions.
Arrays for dynamic commands, `[[ ]]`, `local`, and Bash-specific traps or
options are valid only in this branch.

## POSIX `sh` branch

For `Dialect: POSIX`sh``, follow the shebang convention declared by the target,
use `set -eu` with contextual `-e` caveats, and use scalar variables, positional
parameters, `[ ]`, and `test`. Do not use Bash arrays or `local`; use `pipefail`
only for an explicit POSIX.1-2024 baseline.

## Script-specific operator guidance

- Use `command -v` before first use of required external tools.
- Use structured parsers such as `jq` or `yq` for JSON and YAML when available.
- Prefer `printf` for formatted output and arrays for dynamic commands only in
  the Bash branch.
- Destructive or repeatable scripts should be idempotent and expose `--dry-run` when operator risk is non-trivial.
- Keep operator entrypoints thin and extract repeated branches into sourced helper files only when reuse is real.
- Treat 300 lines as a review threshold and 400 lines as a split-or-justify gate for standalone scripts.
- When script output can grow and the script is agent-facing, prefer bounded summaries by default and add an explicit compact or quiet mode that still preserves blockers, failures, and required next actions.
- Keep full-detail output reachable through an explicit flag or durable artifact path when operators need full diagnostics.

## Testing

- For behavior changes, create the failing focused check before the first implementation edit.
- Prefer the repository's existing Bash harness. Cover parser decisions,
  guards, dry-run behavior, command construction, and rerun safety at their
  stable boundary.
- When the script is documented for direct invocation, that invocation is the
  stable boundary. Reaching the code through an interpreter tests a different
  boundary and leaves the executable bit, the shebang, and `PATH` resolution
  unverified: `bash ./tool.sh` passes where `./tool.sh` fails.
- When no harness can exercise the behavior before editing, record a pre-code testability exception and the alternate validation path. Use syntax, lint,
  and a safe non-mutating invocation as evidence; do not represent later
  regression coverage as test-first work.

## Templates and hardening helpers

After dialect selection, load `references/templates.md` when you need the
starter script, argument parser skeleton, or cleanup helpers. Choose only the
matching Bash or POSIX `sh` section.

- Prefer safe reruns with guards like `mkdir -p`, existence checks, or replace-in-place flows.
- Use `--` before user-supplied paths in destructive commands such as `rm -rf -- "$target"`.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- `bash -n script.sh` (syntax check)
- `shellcheck -s bash script.sh` (lint)
- `shfmt -d script.sh` (format diff, if available)
- `sh -n script.sh` (POSIX `sh` syntax check)
- `shellcheck -s sh script.sh` (POSIX `sh` lint)
