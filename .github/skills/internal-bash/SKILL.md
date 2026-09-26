---
name: internal-bash
description: Use when creating, analyzing, reviewing, or modifying embedded Bash or POSIX `sh`, sourced shell helpers, or non-operator shell fragments that need dialect, safety, quoting, parser, or validation guidance. Route standalone scripts, utilities, wrappers, and launchers to /internal-bash-script.
---

# Internal Bash

## When to use

- Sourced `.sh` helpers, shell snippets, and non-operator shell fragments.
- Shell semantics inside another format, such as a CI `run:` step, a Make
  recipe, or a Dockerfile `RUN`, after that format's owner has claimed the file.
- The dialect, safety, review, and validation baseline that
  `/internal-bash-script` may load for the full catalog and the checker.

## Owner routing

Classify the file before applying rules:

| Evidence | Owner |
| --- | --- |
| Operator entrypoint: shebang with direct invocation, arguments, or usage text | Route to `/internal-bash-script` |
| Sourced file, function library, or shell fragment | This skill |
| Shell embedded in another format | Load that format's owner first; use this skill only for the shell semantics |

## Dialect decision

Classify the shell before applying rules. Preserve an existing declared
interpreter and never silently change it. Record the declared interpreter, the
execution environment, and the compatibility target as the dialect contract:

- `Dialect: Bash` when the caller, entrypoint, runtime, or repository contract
  explicitly provides Bash.
- `Dialect: POSIX sh` when the caller or target requires POSIX shell syntax.

Require an explicit POSIX baseline before treating Issue 8 behavior as
portable. Do not infer portability from Bash invoked as `sh`.

Add `Compatibility target: Bash 3.2` only when the caller or repository
declares macOS `/bin/bash` support. Then avoid `mapfile`, `readarray`,
`declare -A`, `${var,,}`, `${var^^}`, and `wait -n`, and guard an empty-array
expansion under `set -u` with a `${#array[@]}` check. Static checks do not
detect these. Run the target's own harness under `/bin/bash` 3.2 in an isolated
workspace, or report `Bash 3.2 compatibility: unverified`.

## Portable core

- Quote expansions and use explicit status checks at correctness boundaries.
- Prefer `if`, `case`, `test`, and `[ ]` for shared control flow.
- Use `${parameter:?message}` for required values and `$((...))` for arithmetic.
- Use `mktemp` with cleanup traps for temporary state.
- Validate required external commands with `command -v` before first use.
- Use structured parsers such as `jq` or `yq` for JSON and YAML when available.

## Bash branch

For `Dialect: Bash`, follow the deployment shebang convention, normally
`#!/usr/bin/env bash`. Use `set -euo pipefail` with documented exceptions,
arrays for dynamic commands, `[[ ]]`, `local`, and Bash-specific traps or
options.

## POSIX `sh` branch

For `Dialect: POSIX sh`, use the shebang convention declared by the target
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

## Review

For a focused review, load
[references/review-anti-patterns.md](references/review-anti-patterns.md) and
report each finding with its ID, severity, location, and the declared dialect.
A finding that assumes the wrong dialect is not a finding.

## Validation

Run the bundle checker from this skill directory with explicit files:

```bash
scripts/check.sh [--dialect bash|sh] FILE [FILE ...]
```

- The shebang selects the dialect, including `env` options such as
  `#!/usr/bin/env -S bash`. `--dialect` overrides it and is required for a
  file without a shebang, such as a sourced helper.
- `Dialect: Bash` runs `bash -n` and `shellcheck -s bash`. `Dialect: POSIX sh`
  runs `dash -n` and `shellcheck -s sh`; without `dash` it runs `sh -n` and
  reports limited evidence.
- Exit `0` means the checks passed within supported scope, `1` means findings,
  and `2` means a usage, dependency, file, or interpreter failure.
- The checker requires `shellcheck` and the selected interpreter, never
  executes the checked files, bounds each tool's output to 100 lines of 500
  characters, and supports `--self-test` for the bundled fixtures.

The checker does not prove runtime behavior or portability across every
supported `sh`. For behavior changes, also run the repository wrapper or a
focused test under each supported implementation. `shfmt -d FILE` is an
optional format check.
