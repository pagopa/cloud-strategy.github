---
name: internal-script-bash
description: Create or modify Bash scripts with repository-aligned structure plus script-specific hardening for idempotency, dependency checks, and reusable helpers. Use when the user needs shell scripts, automation scripts, helper bash utilities, or any standalone .sh file with reliable operator-facing behavior.
---

# Bash Script Skill

Follow `.github/instructions/internal-bash.instructions.md` for the baseline Bash rules. This skill adds script-specific hardening guidance only.

## When to use
- New Bash scripts.
- Existing Bash scripts that need updates.

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

| Mistake | Why it matters | Instead |
|---|---|---|
| Skipping dependency checks for required commands | Failures surface late and with weaker operator context | Check `command -v` before the first call |
| Building dynamic commands as strings | Quoting and argument boundaries become fragile | Use arrays plus `printf` for operator-facing formatting |
| Destructive commands without rerun safety | Repeated execution can corrupt state or surprise operators | Add `--dry-run` and make the mutation idempotent |
| Rewriting parser or cleanup scaffolding from scratch | Operator UX and failure handling drift between scripts | Reuse the starter and helper patterns from `references/templates.md` |

## Cross-references
- **internal-composite-action** (`.github/skills/internal-composite-action/SKILL.md`): for Bash inside composite actions.
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for reviewing Bash code (see `.github/skills/internal-code-review/references/anti-patterns-bash.md`).

## Validation
- `bash -n script.sh` (syntax check)
- `shellcheck -s bash script.sh` (lint)
- `shfmt -d script.sh` (format diff, if available)
