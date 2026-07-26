# Bash Script Templates

Use this reference when you need a starter script, a CLI parsing pattern, or the standard cleanup helpers.

## Minimal Template

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

log_info()    { printf 'ℹ️  %s\n' "$*"; }
log_warn()    { printf '⚠️  %s\n' "$*"; }
log_success() { printf '✅ %s\n' "$*"; }
log_error()   { printf '❌ %s\n' "$*" >&2; }

main() {
  local target="$DEFAULT_TARGET"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target)
        [[ $# -ge 2 && "$2" != -* ]] || {
          log_error "--target requires a value"
          exit 1
        }
        target="$2"
        shift 2
        ;;
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

## Argument Parsing Pattern

```bash
DEFAULT_SCOPE="repo"
SCOPE="$DEFAULT_SCOPE"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      [[ $# -ge 2 && "$2" != -* ]] || {
        log_error "--scope requires a value"
        exit 1
      }
      SCOPE="$2"
      shift 2
      ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help)   usage; exit 0 ;;
    *)        log_error "Unknown option: $1"; usage; exit 1 ;;
  esac
done
```

## ERR Trap Pattern

```bash
set -eEuo pipefail

on_error() {
  local exit_code=$?
  log_error "Command failed at line ${1:-unknown}: ${2:-unknown} (exit ${exit_code})"
  exit "$exit_code"
}

trap 'on_error "${LINENO}" "${BASH_COMMAND}"' ERR
```

## Hardening Helpers

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
