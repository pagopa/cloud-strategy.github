#!/usr/bin/env bash
#
# Purpose: Bootstrap the local Python environment and run a Copilot maintenance tool.
# Usage examples:
#   ./.github/tools/run.sh build-inventory --root .

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-}"
PYTHON_VERSION_FILE="$REPO_ROOT/.python-version"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

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
    ./.github/tools/run.sh <tool> [tool-args...]

Local tools:
    validate-github-catalog
    benchmark-skill-tokens
    build-inventory
    validate-catalog
    detect-token-risks
    validate-internal-skills
    validate-skill-change-scope

Delegated tools:
    analyze_copilot_debug_log
    sync_home_ai_resources
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

load_required_python_version() {
    if [[ ! -f "$PYTHON_VERSION_FILE" ]]; then
        log_error "Missing required Python version file: $PYTHON_VERSION_FILE"
        exit 1
    fi

    REQUIRED_PYTHON_VERSION="$(tr -d '[:space:]' <"$PYTHON_VERSION_FILE")"
    REQUIRED_PYTHON_MAJOR_MINOR="$(printf '%s' "$REQUIRED_PYTHON_VERSION" | awk -F. 'NF >= 2 { print $1 "." $2 }')"

    if [[ -z "$REQUIRED_PYTHON_MAJOR_MINOR" ]]; then
        log_error "Invalid Python version in $PYTHON_VERSION_FILE: $REQUIRED_PYTHON_VERSION"
        exit 1
    fi
}

select_python_bin() {
    if [[ -n "$PYTHON_BIN" ]]; then
        return
    fi

    PYTHON_BIN="python$REQUIRED_PYTHON_MAJOR_MINOR"
}

verify_python_bin_version() {
    local actual_version
    actual_version="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

    if [[ "$actual_version" == "$REQUIRED_PYTHON_MAJOR_MINOR" ]]; then
        return
    fi

    log_error "$PYTHON_BIN resolved to Python $actual_version, but .python-version requires $REQUIRED_PYTHON_VERSION."
    exit 1
}

verify_venv_version() {
    local venv_python="$VENV_DIR/bin/python"
    local venv_version

    if [[ ! -x "$venv_python" ]]; then
        log_error "Virtual environment is missing its Python interpreter: $venv_python"
        exit 1
    fi

    venv_version="$("$venv_python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    if [[ "$venv_version" == "$REQUIRED_PYTHON_MAJOR_MINOR" ]]; then
        return
    fi

    log_error "Existing virtual environment uses Python $venv_version, but .python-version requires $REQUIRED_PYTHON_VERSION. Remove $VENV_DIR and rerun."
    exit 1
}

resolve_script() {
    local tool_name="$1"
    case "$tool_name" in
        validate-github-catalog|validate-github-catalog.py|validate-github-catalog.sh)
            printf '%s\n' "$SCRIPT_DIR/catalog/validate-github-catalog.py"
            ;;
        analyze_copilot_debug_log|analyze_copilot_debug_log.sh)
            printf '%s\n' "$REPO_ROOT/.github/skills/local-copilot-log-analyzer/scripts/run.sh"
            ;;
        benchmark-skill-tokens|benchmark-skill-tokens.py|benchmark-skill-tokens.sh)
            printf '%s\n' "$REPO_ROOT/.github/scripts/benchmark-skill-tokens.py"
            ;;
        build-inventory|build-inventory.py|build-inventory.sh)
            printf '%s\n' "$SCRIPT_DIR/inventory/build-inventory.py"
            ;;
        validate-catalog|validate-catalog.py|validate-catalog.sh)
            printf '%s\n' "$SCRIPT_DIR/catalog/validate-catalog.py"
            ;;
        detect-token-risks|detect-token-risks.py|detect-token-risks.sh)
            printf '%s\n' "$SCRIPT_DIR/tokens/detect-token-risks.py"
            ;;
        sync_home_ai_resources|sync_home_ai_resources.py)
            printf '%s\n' "$REPO_ROOT/.github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
            ;;
        validate-internal-skills|validate-internal-skills.py|validate-internal-skills.sh)
            printf '%s\n' "$SCRIPT_DIR/skills/validate-internal-skills.py"
            ;;
        validate-skill-change-scope|validate-skill-change-scope.py|validate-skill-change-scope.sh)
            printf '%s\n' "$SCRIPT_DIR/skills/validate-skill-change-scope.py"
            ;;
        *)
            return 1
            ;;
    esac
}

ensure_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        verify_venv_version
        return
    fi
    log_info "Creating local virtual environment."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    verify_venv_version
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

    if [[ "$script_path" == *.sh ]]; then
        exec bash "$script_path" "$@"
    fi

    load_required_python_version
    select_python_bin
    require_command "$PYTHON_BIN"
    verify_python_bin_version
    ensure_venv
    install_dependencies
    exec "$VENV_DIR/bin/python" "$script_path" "$@"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
