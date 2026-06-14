---
description: Bash scripting standards for safe execution, guard clauses, and consistent runtime logs.
applyTo: "**/*.sh"
---

# Bash Instructions

Use this file as the single source of shell guidance for scripts matching `**/*.sh`.

## General principles

- Generate code that is clean, simple, and concise.
- Ensure scripts are easy to read and understand.
- Add comments only where they help explain non-obvious logic.
- Keep runtime output concise and useful.
- Use `shellcheck` for static analysis when available.
- Prefer safe expansions: quote variable references (`"$var"`), use `${var}` for clarity, and avoid `eval`.
- Use modern Bash features (`[[ ]]`, `local`, arrays) when portability requirements allow.
- Choose reliable parsers for structured data instead of ad-hoc text processing.

## Error handling and safety

- Always enable `set -euo pipefail`.
- Validate required parameters before execution.
- Provide clear error messages with context.
- Use `trap` to clean up temporary resources.
- Declare immutable values with `readonly` (or `declare -r`) when appropriate.
- Use `mktemp` for temporary files/directories and clean them in the exit handler.

## Script structure

- Use the Bash shebang: `#!/usr/bin/env bash`.
- Include a short header comment with purpose and usage examples.
- Define defaults near the top of the script.
- Prefer small reusable functions over repeated blocks.
- Keep the main execution flow clean and readable.

## JSON and YAML handling

- Prefer dedicated parsers: `jq` for JSON and `yq` for YAML.
- If those tools are unavailable, choose the next most reliable parser and document it.
- Validate required fields and handle missing paths explicitly.
- Quote parser filters and use raw output mode where needed.
- Treat parser errors as fatal.
- Document parser dependencies and fail fast if missing.

## Repository-specific rules

- Use Bash only: `#!/usr/bin/env bash`.
- Add a short header comment with purpose and usage examples.
- Use emoji logs (`ℹ️ ✅ ⚠️ ❌`) for operator-facing runtime messages.
- Prefer guard clauses and small readable functions over deeply nested control flow.
- Wrapper-style Bash entry points must run successfully with no parameters by keeping the common-path defaults inside the script.
- Optional flags or environment variables may override those defaults; do not require positional arguments for the standard invocation path.
- Apply these rules for both create and modify operations.

## Baseline example

```bash
#!/usr/bin/env bash

set -euo pipefail

cleanup() {
  if [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
  fi
}

trap cleanup EXIT

readonly SCRIPT_NAME="$(basename "$0")"
RESOURCE_GROUP=""
OPTIONAL_PARAM="default-value"
TEMP_DIR=""

usage() {
  echo "Usage: ${SCRIPT_NAME} [OPTIONS]"
  echo "  -g, --resource-group   Resource group (required)"
  echo "  -h, --help             Show this help"
  exit 0
}

validate_requirements() {
  if [[ -z "${RESOURCE_GROUP}" ]]; then
    echo "Error: resource group is required" >&2
    exit 1
  fi
}

main() {
  validate_requirements
  TEMP_DIR="$(mktemp -d)"
  echo "ℹ️ Starting script execution"
  echo "✅ Completed successfully"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--resource-group)
      RESOURCE_GROUP="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

main "$@"
```

## Minimal delta example

```bash
#!/usr/bin/env bash
#
# Purpose: Explain what this script does.
# Usage examples:
#   ./script.sh
#   ./script.sh --target custom-target

set -euo pipefail

DEFAULT_TARGET="default-target"

main() {
  local target="${DEFAULT_TARGET}"

  echo "ℹ️  Processing ${target}"
}

main "$@"
```

## Python launcher additions

- When the Bash script is a launcher for a standalone Python tool, use it only when that tool needs external packages or an isolated local bootstrap path.
- Python launchers must keep the common invocation path zero-argument friendly by embedding sensible default Python-script parameters and exposing only optional overrides.
- For those Python launchers, resolve the script directory, create or reuse a sibling `.venv`, install from the local hash-locked `requirements.txt`, and execute the sibling Python entry point.

## Validation

- `bash -n <script>.sh`
- `shellcheck -s bash <script>.sh` (if available)
