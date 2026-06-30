---
name: internal-bash-script
description: Use when creating or modifying standalone Bash scripts or shell utilities with operator-facing behavior, rather than Bash embedded inside composite actions or CI workflows.
---

# Bash Script Skill

## Referenced skills

- `internal-github-action-composite`: route Bash embedded in GitHub composite actions.
- `internal-github-actions`: route GitHub workflow-level behavior.

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
- Keep operator entrypoints thin and extract repeated branches into sourced helper files only when reuse is real.
- Treat 300 lines as a review threshold and 400 lines as a split-or-justify gate for standalone scripts.
- When script output can grow and the script is agent-facing, prefer bounded summaries by default and add an explicit compact or quiet mode that still preserves blockers, failures, and required next actions.
- Keep full-detail output reachable through an explicit flag or durable artifact path when operators need full diagnostics.
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
