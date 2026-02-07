---
applyTo: "**/*.sh"
---

# Bash Instructions

## Mandatory rule
- `.sh` files must use Bash, not POSIX `sh`.

## Standard header
```bash
#!/usr/bin/env bash
set -euo pipefail
```

## Logging functions
```bash
log_info()    { echo "INFO: $*"; }
log_success() { echo "SUCCESS: $*"; }
log_error()   { echo "ERROR: $*" >&2; }
```

## Best practices
- Quote all variables: `"$var"`.
- Use `[[ ... ]]` for conditionals.
- Use `$(command)` instead of backticks.
- Check dependencies with `command -v tool >/dev/null 2>&1`.

## Recommended structure
```bash
main() {
  log_info "Starting script"
  # implementation
  log_success "Completed"
}

main "$@"
```

## Validation
- Run `bash -n <script>.sh`.
- Run `shellcheck -s bash <script>.sh` when available.
