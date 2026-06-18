---
name: internal-bash
description: Use when editing shell or Bash files that need lightweight safety, quoting, parser, or validation guidance.
---

# Internal Bash

## Referenced skills

Treat the referenced skill below as an on-demand owner. Do not preload it just
because the file is Bash; load it only when the task shifts from embedded shell
safety to standalone script behavior.

- `internal-bash-script`: standalone Bash scripts, shell utilities, wrappers, launchers, and operator-facing behavior.

## When to use

- `.sh` files and Bash snippets where the main need is a shared safety baseline.
- Shell embedded in repository automation when no narrower owner has stronger rules.
- Quick checks for quoting, strict mode, guard clauses, temp files, and parser choices.

## When not to use

- Standalone script design, launcher behavior, operator UX, or script templates; use `internal-bash-script`.
- Bash embedded in GitHub composite actions; use `internal-github-action-composite`.
- GitHub workflow-level behavior; use `internal-github-actions`.

## Baseline

- Prefer `#!/usr/bin/env bash` for repository-owned Bash scripts.
- Use `set -euo pipefail` unless the script has a documented compatibility reason.
- Treat 300 lines as a review threshold for cohesive shell files.
- Treat 400 lines as a split-or-justify threshold and extract sourced helpers when repeated decisions or branches degrade readability.
- Apply pragmatic DRY: de-duplicate repeated decision paths, but keep one-off logic local when extraction harms auditability.
- Quote variable expansions and use arrays for dynamic commands.
- Prefer `[[ ]]`, `local`, and readable guard clauses when Bash is available.
- Use `mktemp` plus cleanup traps for temporary state.
- Validate required external commands with `command -v` before first use.
- Use structured parsers such as `jq` or `yq` for JSON and YAML when available.

## Validation

- `bash -n <script>.sh` for syntax.
- `shellcheck -s bash <script>.sh` when available.
- Run the repository wrapper or focused script command when behavior changes.
