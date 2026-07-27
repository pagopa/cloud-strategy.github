---
name: internal-bash
description: Use when creating, analyzing, reviewing, or modifying embedded Bash or POSIX `sh`, sourced shell helpers, or non-operator shell fragments that need dialect, safety, quoting, parser, or validation guidance.
---

# Internal Bash

## Referenced files

- `references/review-anti-patterns.md`: Bash review anti-pattern catalog with
  ID-tagged patterns, severity, rationale, and examples. Load for focused review
  of shell content within this skill's scope.

## When to use

- Review or modification of sourced `.sh` helpers and Bash snippets where the
  main need is a shared safety baseline.
- Shell embedded in repository automation when no narrower owner has stronger rules.
- Non-operator Bash helpers that do not own a standalone operator entrypoint.
- Quick checks for quoting, strict mode, guard clauses, temp files, and parser choices.

## When not to use

- Standalone script design, standalone script review, launcher behavior,
  operator UX, or script templates.
- Shell embedded in an automation format whose enclosing platform contract is
  the primary subject.
- Workflow-level behavior beyond the shell fragment itself.

## Dialect decision

Classify the shell before applying rules. Preserve an existing declared
interpreter and never silently change it. Record the declared interpreter, the
execution environment, and the compatibility target as the dialect contract:

- `Dialect: Bash` when the caller, entrypoint, runtime, or repository contract
  explicitly provides Bash.
- `Dialect: POSIX `sh`` when the caller or target requires POSIX shell syntax.

Require an explicit POSIX baseline before treating Issue 8 behavior as
portable. Do not infer portability from Bash invoked as `sh`.

## Portable core

- Quote expansions and use explicit status checks at correctness boundaries.
- Prefer `if`, `case`, `test`, and `[ ]` for shared control flow.
- Use `${parameter:?message}` for required values and `$((...))` for arithmetic.
- Use `mktemp` with cleanup traps for temporary state.
- Validate required external commands with `command -v` before first use.
- Use structured parsers such as `jq` or `yq` for JSON and YAML when available.

## Bash branch

For `Dialect: Bash`, use the repository shebang convention
`#!/usr/bin/env bash`, `set -euo pipefail` with documented exceptions, arrays
for dynamic commands, `[[ ]]`, `local`, and Bash-specific traps or options.

## POSIX `sh` branch

For `Dialect: POSIX `sh``, use the shebang convention declared by the target
repository or platform. Use `set -eu` with contextual `-e` caveats, scalar
variables and positional parameters, and `[ ]` or `test`. Do not use Bash arrays
or `local`. Use `pipefail` only when POSIX.1-2024 Issue 8 is an explicit
baseline; it is not a safe assumption for an unspecified `/bin/sh`.

## File design

- Treat 300 lines as a review threshold for cohesive shell files.
- Treat 400 lines as a split-or-justify threshold and extract sourced helpers
  when repeated decisions or branches degrade readability.
- Apply pragmatic DRY: de-duplicate repeated decision paths, but keep one-off
  logic local when extraction harms auditability.

## Validation

For `Dialect: Bash`, run `bash -n <script>.sh` and
`shellcheck -s bash <script>.sh` when available. For `Dialect: POSIX `sh``, run
`sh -n <script>.sh`, `shellcheck -s sh <script>.sh`, and execute under each
repository-supported `sh` implementation. Bash invoked as `sh` is not
cross-shell portability proof. Run the repository wrapper or focused command
when behavior changes.
