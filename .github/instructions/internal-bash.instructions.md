---
description: Bash scripting standards for safe execution, guard clauses, and consistent runtime logs.
applyTo: "**/*.sh"
---

<!-- Core Knowledge Source: awesome-copilot-shell.instructions.md -->
<!-- This internal instruction extends the external with governance-specific rules. -->
<!-- Do not duplicate content from the core source; reference it instead. -->

# Bash Instructions

## Mandatory rules
- Use Bash only: `#!/usr/bin/env bash`.
- Add a header comment with purpose and usage examples.
- Use emoji logs (`ℹ️ ✅ ⚠️ ❌`) for runtime visibility.
- Prefer early return and simple, readable functions.
- Wrapper-style Bash entry points must run successfully with no parameters by keeping the common-path defaults inside the script.
- Optional flags or environment variables may override those defaults; do not require arguments for the standard invocation path.
- Apply these rules for both create and modify operations.

## Standard skeleton
```bash
#!/usr/bin/env bash
#
# Purpose: Explain what this script does.
# Usage examples:
#   ./script.sh
#   ./script.sh --help
#   ./script.sh --target custom-target


set -euo pipefail

DEFAULT_TARGET="default-target"

usage() {
  cat <<'EOF'
Usage:
  ./script.sh [--target value]
EOF
}

main() {
  local target="${DEFAULT_TARGET}"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target)
        target="${2:?❌ --target requires a value}"
        shift 2
        ;;
      --help)
        usage
        exit 0
        ;;
      *)
        echo "❌ Unknown option: $1" >&2
        usage
        exit 1
        ;;
    esac
  done

  echo "ℹ️  Processing ${target}"
}

main "$@"
```

## Repository-specific additions
- When the Bash script is a launcher for a standalone Python tool, use it only when that tool needs external packages or an isolated local bootstrap path.
- Python launchers must keep the common invocation path zero-argument friendly by embedding sensible default Python-script parameters and exposing only optional overrides.
- For those Python launchers, resolve the script directory, create or reuse a sibling `.venv`, install from the local hash-locked `requirements.txt`, and execute the sibling Python entry point.

## Validation
- `bash -n <script>.sh`
- `shellcheck -s bash <script>.sh` (if available)
