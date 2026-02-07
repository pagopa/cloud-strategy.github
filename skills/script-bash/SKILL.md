---
name: script-bash
description: Create Bash scripts with logging, error handling, and minimum validation.
---

# Bash Script Skill

## When to use
- Simple file or directory operations.
- CLI wrappers.
- Local environment setup.
- Quick automation tasks.

## Mandatory rule
- `.sh` files must use Bash (`#!/usr/bin/env bash`).
- Do not use POSIX `sh` in generated templates.

## Template

```bash
#!/usr/bin/env bash
#
# {script_name}.sh
# Purpose: {description}
# Usage: ./{script_name}.sh [options]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

log_info()    { echo "INFO: $*"; }
log_success() { echo "SUCCESS: $*"; }
log_error()   { echo "ERROR: $*" >&2; }
log_warning() { echo "WARNING: $*"; }

usage() {
    cat << EOF
Usage: $(basename "$0") [options]

Options:
  -h, --help      Show this help message
  -v, --verbose   Enable verbose output
EOF
}

main() {
  log_info "Starting {script_name}"

  # Implementation here

  log_success "Completed"
}

main "$@"
```

## Checklist
- [ ] `set -euo pipefail` is present.
- [ ] Variables are always quoted.
- [ ] Logging functions are used.
- [ ] Usage/help function is present.
- [ ] Validation includes `bash -n` and `shellcheck -s bash`.
