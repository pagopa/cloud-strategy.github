---
applyTo: "**/*.sh"
---

# Bash Instructions

## Mandatory rules
- `.sh` files must use Bash, not POSIX `sh`.
- Start each script with a comment block that explains purpose and usage examples.
- Use emoji logs to make execution flow easy to follow.
- Prefer early return and simple, readable functions.

## Standard header
```bash
#!/usr/bin/env bash
#
# Purpose: Explain what this script does.
# Usage examples:
#   ./script.sh --help
#   ./script.sh --input data.json

set -euo pipefail
```

## Logging functions
```bash
log_info()    { echo "ℹ️  $*"; }
log_success() { echo "✅ $*"; }
log_warn()    { echo "⚠️  $*"; }
log_error()   { echo "❌ $*" >&2; }
```

## Best practices
- Quote all variables: `"$var"`.
- Use `[[ ... ]]` for conditionals.
- Use `$(command)` instead of backticks.
- Check dependencies with `command -v tool >/dev/null 2>&1`.
- Keep functions short and focused.

## Recommended structure
```bash
parse_args() {
  if [[ $# -eq 0 ]]; then
    log_error "No arguments provided"
    return 1
  fi

  if [[ "${1:-}" == "--help" ]]; then
    usage
    return 1
  fi

  return 0
}

main() {
  log_info "🚀 Starting script"

  if ! parse_args "$@"; then
    return 1
  fi

  # implementation

  log_success "🏁 Completed"
}

main "$@"
```

## Validation
- Run `bash -n <script>.sh`.
- Run `shellcheck -s bash <script>.sh` when available.
