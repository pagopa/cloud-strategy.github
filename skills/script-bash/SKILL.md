---
name: script-bash
description: Create Bash scripts with purpose header, emoji logs, early return patterns, and strong readability.
---

# Bash Script Skill

## When to use
- Simple file or directory operations.
- CLI wrappers.
- Local environment setup.
- Quick automation tasks.
- Creating new scripts and modifying existing Bash scripts.

## Mandatory rules
- `.sh` files must use Bash (`#!/usr/bin/env bash`).
- Do not use POSIX `sh` in generated templates.
- Start with a script comment block that describes purpose and usage examples.
- Use emoji logs to make runtime behavior clear.
- Prefer early return and guard clauses.
- Apply these rules both to new files and existing files being modified.

## Template

```bash
#!/usr/bin/env bash
#
# Purpose: {description}
# Usage examples:
#   ./{script_name}.sh --help
#   ./{script_name}.sh --input data.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

log_info()    { echo "ℹ️  $*"; }
log_success() { echo "✅ $*"; }
log_warn()    { echo "⚠️  $*"; }
log_error()   { echo "❌ $*" >&2; }

usage() {
  cat << 'USAGE'
Usage: $(basename "$0") [options]

Options:
  -h, --help         Show this help message
  -i, --input PATH   Input path
USAGE
}

parse_args() {
  if [[ $# -eq 0 ]]; then
    log_error "Missing arguments"
    usage
    return 1
  fi

  if [[ "${1:-}" == "--help" ]]; then
    usage
    return 1
  fi

  return 0
}

main() {
  log_info "🚀 Starting {script_name}"

  if ! parse_args "$@"; then
    return 1
  fi

  # Implementation here

  log_success "🏁 Completed"
}

main "$@"
```

## Checklist
- [ ] `set -euo pipefail` is present.
- [ ] Variables are always quoted.
- [ ] Purpose and usage examples are in the script header.
- [ ] Emoji logging is used consistently.
- [ ] Early return guards are used.
- [ ] Validation includes `bash -n` and `shellcheck -s bash`.
