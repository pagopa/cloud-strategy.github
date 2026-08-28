#!/usr/bin/env bash
#
# Purpose: Run the self-contained Copilot debug-log analyzer.
# Usage examples:
#   bash scripts/run.sh prompt-exports exports.json
#   bash scripts/run.sh debug-logs log.json --format markdown

set -Eeuo pipefail

log_error() {
    printf 'Error: %s\n' "$*" >&2
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        log_error "missing required command: $1"
        exit 1
    }
}

usage() {
    cat <<'EOF'
Usage:
    bash scripts/run.sh <prompt-exports|debug-logs> [args...]

Examples:
    bash scripts/run.sh prompt-exports exports.json
    bash scripts/run.sh debug-logs log.json --format markdown
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
    log_error "missing SHA-256 helper: install sha256sum or shasum"
    exit 1
}

ensure_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        if [[ -x "$VENV_DIR/bin/python" ]]; then
            return
        fi
        rm -rf "$VENV_DIR"
    fi

    "$PYTHON_BIN" -m venv "$VENV_DIR"
}

install_dependencies() {
    local requirements_hash
    local current_hash

    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_error "missing requirements file: $REQUIREMENTS_FILE"
        exit 1
    fi

    requirements_hash="$(hash_file "$REQUIREMENTS_FILE")"
    current_hash=""
    if [[ -f "$REQUIREMENTS_HASH_FILE" ]]; then
        current_hash="$(<"$REQUIREMENTS_HASH_FILE")"
    fi

    if [[ "$requirements_hash" == "$current_hash" ]]; then
        return
    fi

    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
    printf '%s' "$requirements_hash" >"$REQUIREMENTS_HASH_FILE"
}

main() {
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || $# -eq 0 ]]; then
        usage
        if [[ $# -eq 0 ]]; then
            exit 1
        fi
        exit 0
    fi

    PYTHON_BIN="${PYTHON_BIN:-python3}"
    require_command "$PYTHON_BIN"
    ensure_venv
    install_dependencies
    PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}" \
        exec "$VENV_DIR/bin/python" -m analyze_copilot_debug_log "$@"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-}"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

main "$@"
