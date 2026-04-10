---
name: internal-script-bash
description: Create or modify Bash scripts with purpose header, emoji logs, readable guard-clause flow, and defensive hardening for cleanup traps, temp resources, and safe reruns. Use when the user needs shell scripts, automation scripts, helper bash utilities, or any standalone .sh file with reliable failure handling and structured output.
---

# Bash Script Skill

Follow `.github/instructions/internal-bash.instructions.md` for the baseline Bash rules. This skill adds script-specific hardening guidance only.

## When to use
- New Bash scripts.
- Existing Bash scripts that need updates.

## Script-specific hardening guidance
- Quote all variables: `"$var"`, never bare `$var`.
- Prefer `printf` for formatted output and arrays for dynamic commands.
- Use `mktemp` plus a cleanup trap for temporary files or directories when the script owns temporary state.
- Destructive or repeatable scripts should be idempotent and expose `--dry-run` when operator risk is non-trivial.
- Validate required external commands with `command -v` before first use.
- Do not add unit tests unless explicitly requested.

## Minimal template
```bash
#!/usr/bin/env bash
#
# Purpose: {description}
# Usage examples:
#   ./{script_name}.sh
#   ./{script_name}.sh --help
#   ./{script_name}.sh --target custom-target

set -euo pipefail

DEFAULT_TARGET="default-target"

log_info()    { echo "ℹ️  $*"; }
log_warn()    { echo "⚠️  $*"; }
log_success() { echo "✅ $*"; }
log_error()   { echo "❌ $*" >&2; }

main() {
  local target="$DEFAULT_TARGET"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target) target="${2:?❌ --target requires a value}"; shift 2 ;;
      --help) usage; exit 0 ;;
      *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
  done

  log_info "Processing $target"
  # ... logic ...
  log_success "Done"
}

usage() {
  cat <<'EOF'
Usage:
  ./{script_name}.sh [--target value]
EOF
}

main "$@"
```

## Argument parsing pattern
```bash
DEFAULT_SCOPE="repo"
SCOPE="$DEFAULT_SCOPE"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)  SCOPE="${2:?❌ --scope requires a value}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help)   usage; exit 0 ;;
    *)        log_error "Unknown option: $1"; usage; exit 1 ;;
  esac
done
```

## Hardening patterns
```bash
require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    log_error "Missing required command: $1"
    exit 1
  }
}

cleanup() {
  [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]] || return 0
  rm -rf -- "$TMP_DIR"
}

TMP_DIR="$(mktemp -d)"
trap cleanup EXIT
```

- Use `mktemp` and `trap cleanup EXIT` only when the script owns temporary state.
- Prefer safe reruns with guards like `mkdir -p`, existence checks, or replace-in-place flows.
- Use `--` before user-supplied paths in destructive commands such as `rm -rf -- "$target"`.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Missing `set -euo pipefail` | Errors silently ignored, script continues in broken state | Always first executable line |
| Unquoted variables: `$var` | Word splitting and glob expansion cause bugs with spaces/special chars | Always `"$var"` |
| Using `eval` | Command injection risk | Use arrays for dynamic commands: `cmd=("${parts[@]}"); "${cmd[@]}"` |
| Piping to `while read` without process substitution | Loop runs in subshell — variable changes lost | Use `while read ... done < <(command)` |
| No `main()` function wrapper | Global scope pollution, no clean entry point | Wrap logic in `main()` and call `main "$@"` |
| Temporary files without cleanup | Leaks state and leaves partial artifacts behind | Use `mktemp` plus `trap cleanup EXIT` |
| Destructive commands without rerun safety | Repeated execution can corrupt state or surprise operators | Add `--dry-run` and make the mutation idempotent |
| Hardcoded paths | Non-portable across environments | Use variables or `dirname "$0"` for relative paths |
| Wrapper requires positional arguments for the default path | Makes the common invocation brittle and hard to automate | Keep sane defaults in the script and expose optional overrides |

## Cross-references
- **internal-composite-action** (`.github/skills/internal-composite-action/SKILL.md`): for Bash inside composite actions.
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for reviewing Bash code (see `.github/skills/internal-code-review/references/anti-patterns-bash.md`).

## Validation
- `bash -n script.sh` (syntax check)
- `shellcheck -s bash script.sh` (lint)
- `shfmt -d script.sh` (format diff, if available)
