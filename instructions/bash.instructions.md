---
applyTo: "**/*.sh"
---

# Bash Instructions

## Header
```bash
#!/usr/bin/env bash
set -euo pipefail
```

## Logging Functions
```bash
log_info()    { echo "🔍 $*"; }
log_success() { echo "✅ $*"; }
log_error()   { echo "❌ $*" >&2; }
```

## Best Practices
- Quote all variables: `"$var"` not `$var`
- Use `[[ ]]` for conditionals
- Use `$(command)` not backticks
- Check command existence: `command -v tool &>/dev/null`

## Structure
```bash
main() {
    log_info "Starting script"
    # implementation
    log_success "Completed"
}

main "$@"
```
