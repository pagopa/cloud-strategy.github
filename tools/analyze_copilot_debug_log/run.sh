#!/usr/bin/env bash
#
# Purpose: Run the self-contained Copilot debug-log analyzer.
# Usage examples:
#   bash tools/analyze_copilot_debug_log/run.sh prompt-exports exports.json
#   bash tools/analyze_copilot_debug_log/run.sh debug-logs log.json --format markdown

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
  bash tools/analyze_copilot_debug_log/run.sh <prompt-exports|debug-logs> [args...]

Examples:
  bash tools/analyze_copilot_debug_log/run.sh prompt-exports exports.json
  bash tools/analyze_copilot_debug_log/run.sh debug-logs log.json --format markdown
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

load_required_python_version() {
    if [[ ! -f "$PYTHON_VERSION_FILE" ]]; then
        log_error "missing Python version file: $PYTHON_VERSION_FILE"
        exit 1
    fi

    REQUIRED_PYTHON_VERSION="$(tr -d '[:space:]' <"$PYTHON_VERSION_FILE")"
    REQUIRED_PYTHON_MAJOR_MINOR="$(printf '%s' "$REQUIRED_PYTHON_VERSION" | awk -F. 'NF >= 2 { print $1 "." $2 }')"

    if [[ -z "$REQUIRED_PYTHON_MAJOR_MINOR" ]]; then
        log_error "invalid Python version in $PYTHON_VERSION_FILE: $REQUIRED_PYTHON_VERSION"
        exit 1
    fi
}

select_python_bin() {
    if [[ -n "$PYTHON_BIN" ]]; then
        PYTHON_BIN_EXPLICIT=1
        return
    fi
    PYTHON_BIN_EXPLICIT=0
    PYTHON_BIN="python$REQUIRED_PYTHON_MAJOR_MINOR"
}

verify_python_bin_version() {
    local actual_version
    actual_version="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

    if [[ "$actual_version" == "$REQUIRED_PYTHON_MAJOR_MINOR" ]]; then
        EXPECTED_PYTHON_MAJOR_MINOR="$REQUIRED_PYTHON_MAJOR_MINOR"
        return
    fi

    if [[ "$PYTHON_BIN_EXPLICIT" -eq 1 ]]; then
        EXPECTED_PYTHON_MAJOR_MINOR="$actual_version"
        return
    fi

    log_error "$PYTHON_BIN resolved to Python $actual_version, but .python-version requires $REQUIRED_PYTHON_VERSION"
    exit 1
}

verify_venv_version() {
    local venv_python="$VENV_DIR/bin/python"
    local venv_version

    if [[ ! -x "$venv_python" ]]; then
        return 1
    fi

    venv_version="$($venv_python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    if [[ "$venv_version" == "$EXPECTED_PYTHON_MAJOR_MINOR" ]]; then
        return 0
    fi

    return 1
}

ensure_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        if verify_venv_version; then
            return
        fi
        rm -rf "$VENV_DIR"
    fi

    "$PYTHON_BIN" -m venv "$VENV_DIR"
    if ! verify_venv_version; then
        log_error "virtual environment uses an unexpected Python version after creation: $VENV_DIR"
        exit 1
    fi
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

    load_required_python_version
    select_python_bin
    require_command "$PYTHON_BIN"
    verify_python_bin_version
    ensure_venv
    install_dependencies
    cd "$REPO_ROOT"
    exec "$VENV_DIR/bin/python" -m tools.analyze_copilot_debug_log "$@"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-}"
PYTHON_BIN_EXPLICIT=0
EXPECTED_PYTHON_MAJOR_MINOR=""
PYTHON_VERSION_FILE="$REPO_ROOT/.python-version"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

main "$@"
