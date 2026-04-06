#!/usr/bin/env bash
#
# Purpose: Bootstrap the local Python environment and run a Copilot maintenance tool.
# Usage examples:
#   ./.github/scripts/run.sh build_inventory --root .
#   ./.github/scripts/run.sh sync_copilot_catalog plan --target-repo ../consumer-repo

set -Eeuo pipefail

log_info() {
    printf 'ℹ️  %s\n' "$*"
}

log_success() {
    printf '✅ %s\n' "$*"
}

log_error() {
    printf '❌ %s\n' "$*" >&2
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        log_error "Missing required command: $1"
        exit 1
    }
}

usage() {
    cat <<'EOF'
Usage:
  ./.github/scripts/run.sh <tool> [tool-args...]

Tools:
  build_inventory
  check_catalog_consistency
  audit_copilot_catalog
  detect_token_risks
  sync_copilot_catalog
EOF
}

hash_file() {
    local file_path="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$file_path" | awk '{print $1}'
        return
    fi
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$file_path" | awk '{print $1}'
        return
    fi
    log_error "Missing SHA-256 helper: install sha256sum or shasum."
    exit 1
}

resolve_script() {
    local tool_name="$1"
    case "$tool_name" in
        build_inventory|build_inventory.py)
            printf '%s\n' "$SCRIPT_DIR/build_inventory.py"
            ;;
        check_catalog_consistency|check_catalog_consistency.py)
            printf '%s\n' "$SCRIPT_DIR/check_catalog_consistency.py"
            ;;
        audit_copilot_catalog|audit_copilot_catalog.py)
            printf '%s\n' "$SCRIPT_DIR/audit_copilot_catalog.py"
            ;;
        detect_token_risks|detect_token_risks.py)
            printf '%s\n' "$SCRIPT_DIR/detect_token_risks.py"
            ;;
        sync_copilot_catalog|sync_copilot_catalog.py)
            printf '%s\n' "$SCRIPT_DIR/sync_copilot_catalog.py"
            ;;
        *)
            return 1
            ;;
    esac
}

ensure_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        return
    fi
    log_info "Creating local virtual environment."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
}

install_dependencies() {
    local requirements_hash
    local current_hash
    requirements_hash="$(hash_file "$REQUIREMENTS_FILE")"
    current_hash=""

    if [[ -f "$REQUIREMENTS_HASH_FILE" ]]; then
        current_hash="$(<"$REQUIREMENTS_HASH_FILE")"
    fi

    if [[ "$requirements_hash" == "$current_hash" ]]; then
        return
    fi

    log_info "Installing locked Python dependencies."
    "$VENV_DIR/bin/pip" install --require-hashes -r "$REQUIREMENTS_FILE"
    printf '%s' "$requirements_hash" >"$REQUIREMENTS_HASH_FILE"
    log_success "Local Python environment is ready."
}

main() {
    local tool_name="${1:-}"
    local script_path=""

    if [[ -z "$tool_name" ]]; then
        usage
        exit 1
    fi

    script_path="$(resolve_script "$tool_name")" || {
        log_error "Unknown tool: $tool_name"
        usage
        exit 1
    }
    shift

    require_command "$PYTHON_BIN"
    ensure_venv
    install_dependencies
    exec "$VENV_DIR/bin/python" "$script_path" "$@"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

main "$@"
