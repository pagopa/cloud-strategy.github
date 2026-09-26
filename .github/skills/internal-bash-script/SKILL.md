---
name: internal-bash-script
description: Use when creating, reviewing, or modifying standalone Bash or POSIX `sh` scripts, utilities, wrappers, launchers, or other operator-facing shell entrypoints. Route embedded shell fragments and sourced helpers inside another program to /internal-bash.
---

# Internal Bash Script

## When to use

- Creating, reviewing, or modifying a standalone Bash or POSIX `sh` script,
  utility, wrapper, launcher, or other operator entrypoint.
- Route sourced helpers and shell fragments to `/internal-bash`. Route shell
  embedded in another format to that format's owner first.

## Dialect minimum

Record the dialect contract before choosing a template: the declared
interpreter, the execution environment, and the compatibility target. Preserve
the declared interpreter and never change it silently.

- `Dialect: Bash`: follow the deployment shebang convention, normally
  `#!/usr/bin/env bash`. Use `set -euo pipefail` with documented exceptions.
  Arrays, `[[ ]]`, and `local` are valid only here.
- `Dialect: POSIX sh`: follow the target's shebang convention. Use `set -eu`,
  scalar variables, positional parameters, and `[ ]` or `test`. Do not use
  arrays or `local`. Use `pipefail` only with an explicit POSIX.1-2024
  baseline.

Bash invoked as `sh` is not cross-shell portability proof.

## Portable minimum

- Quote expansions and check statuses at correctness boundaries.
- Validate required external commands with `command -v` before first use.
- Use `mktemp` with cleanup traps for temporary state.
- Use structured parsers such as `jq` or `yq` for JSON and YAML when available.

For the full anti-pattern catalog, owner-routing table, and the static
checker, load `/internal-bash` when it is available.

## Operator guidance

- Prefer `printf` for formatted output.
- Destructive or repeatable scripts should be idempotent and expose
  `--dry-run` when operator risk is non-trivial.
- Prefer safe reruns with guards like `mkdir -p`, existence checks, or
  replace-in-place flows.
- Use `--` before user-supplied paths in destructive commands such as
  `rm -rf -- "$target"`.
- Keep operator entrypoints thin and extract repeated branches into sourced
  helper files only when reuse is real.
- Treat 300 lines as a review threshold and 400 lines as a split-or-justify
  gate for standalone scripts.
- Preserve an existing `--format compact` option, payload, and consumers.
  Consider a terminal-only `--compact` projection only for a new interface
  with measured high output volume.

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

## References

- [references/templates.md](references/templates.md): load after the dialect
  decision for the starter script, argument parser, ERR trap, or cleanup
  helpers. Use only the section that matches the dialect.
- [references/operator-output.md](references/operator-output.md): load for
  multi-step lifecycle output, bounded diagnostics, compact, quiet, and verbose
  behavior, and failure continuation.
- [references/common-mistakes.md](references/common-mistakes.md): load before
  finishing any script creation, modification, or review.

## Validation

- `Dialect: Bash`: run `bash -n FILE` and `shellcheck -s bash FILE`.
- `Dialect: POSIX sh`: run `dash -n FILE` (or `sh -n FILE`, reported as
  limited evidence) and `shellcheck -s sh FILE`.
- When `/internal-bash` is loaded, its static checker runs these checks with a
  stable exit contract.
- Run a safe, non-mutating direct invocation, such as `./tool.sh --help`, to
  verify the executable bit, the shebang, and the argument parser.
- `shfmt -d FILE` is an optional format check.
