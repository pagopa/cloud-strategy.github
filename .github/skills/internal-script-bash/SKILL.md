---
name: internal-script-bash
description: Use when creating or modifying standalone Bash scripts or shell utilities with operator-facing behavior, rather than Bash embedded inside composite actions or CI workflows.
---

# Bash Script Skill

## When to use

- New Bash scripts.
- Existing Bash scripts that need updates.

## When not to use

- Bash embedded in GitHub composite actions; use `internal-github-action-composite`.
- GitHub workflow-level behavior; use `internal-github-actions`.

## Compact Bash baseline

- Prefer `#!/usr/bin/env bash` for repository-owned Bash scripts.
- Use `set -euo pipefail` unless the script has a documented compatibility reason.
- Quote variable expansions and use arrays for dynamic commands.
- Prefer `[[ ]]`, `local`, and readable guard clauses when Bash is available.
- Use `mktemp` plus cleanup traps for temporary state.
- Validate required external commands with `command -v` before first use.
- Use structured parsers such as `jq` or `yq` for JSON and YAML when available.

## Script-specific hardening guidance

- Prefer `printf` for formatted output and arrays for dynamic commands.
- Destructive or repeatable scripts should be idempotent and expose `--dry-run` when operator risk is non-trivial.
- Validate required external commands with `command -v` before first use.
- Do not add unit tests unless explicitly requested.

## Templates and hardening helpers

Load `references/templates.md` when you need the starter script, the standard argument parser skeleton, or optional cleanup helpers for scripts that own temporary state.

- Prefer safe reruns with guards like `mkdir -p`, existence checks, or replace-in-place flows.
- Use `--` before user-supplied paths in destructive commands such as `rm -rf -- "$target"`.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- `bash -n script.sh` (syntax check)
- `shellcheck -s bash script.sh` (lint)
- `shfmt -d script.sh` (format diff, if available)
