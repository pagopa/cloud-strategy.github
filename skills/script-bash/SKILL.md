---
name: script-bash
description: Create Bash scripts with proper error handling and logging. Use for simple automation and shell operations.
---

# Bash Script Skill

## When to Use
- Simple file operations
- Wrapper scripts for tools
- Environment setup
- Quick automation tasks

## Template

```bash
#!/usr/bin/env bash
#
# 📋 {script_name}.sh
# 🎯 Purpose: {description}
# 📖 Usage: ./{script_name}.sh [options]
#

set -euo pipefail

# ==============================================================================
# Configuration
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

# ==============================================================================
# Logging
# ==============================================================================

log_info()    { echo "🔍 $*"; }
log_success() { echo "✅ $*"; }
log_error()   { echo "❌ $*" >&2; }
log_warning() { echo "⚠️  $*"; }

# ==============================================================================
# Functions
# ==============================================================================

usage() {
    cat << EOF
Usage: $(basename "$0") [options]

Options:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output

EOF
}

# ==============================================================================
# Main
# ==============================================================================

main() {
    log_info "Starting {script_name}"
    
    # Implementation here
    
    log_success "Completed"
}

main "$@"
```

## Checklist
- [ ] `set -euo pipefail` at the top
- [ ] All variables quoted
- [ ] Logging functions used
- [ ] Usage/help function
- [ ] Error handling for critical operations
