#!/usr/bin/env bash
#
# Purpose: Bootstrap the local Python environment and run a Copilot maintenance tool.
# Usage examples:
#   ./.github/scripts/run.sh build_inventory --root .

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
    github_catalog_validation
    analyze_copilot_debug_log
    benchmark_skill_tokens
  build_inventory
  check_catalog_consistency
  audit_copilot_catalog
  detect_token_risks
    sync_home_ai_resources
  validate_critical_output
    validate_internal_skills
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
        github_catalog_validation|github_catalog_validation.py)
            printf '%s\n' "$SCRIPT_DIR/github_catalog_validation.py"
            ;;
        analyze_copilot_debug_log|analyze_copilot_debug_log.sh)
            printf '%s\n' "$REPO_ROOT/tools/analyze_copilot_debug_log/run.sh"
            ;;
        benchmark_skill_tokens|benchmark_skill_tokens.py)
            printf '%s\n' "$SCRIPT_DIR/benchmark_skill_tokens.py"
            ;;
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
        sync_home_ai_resources|sync_home_ai_resources.py)
            printf '%s\n' "$REPO_ROOT/.github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
            ;;
        validate_critical_output)
            printf '%s\n' "$REPO_ROOT/.github/skills/internal-gateway-critical-master/scripts/validate_critical_output.py"
            ;;
        validate_internal_skills|validate_internal_skills.py)
            printf '%s\n' "$SCRIPT_DIR/validate_internal_skills.py"
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

    if [[ "$tool_name" == "analyze_copilot_debug_log" || "$tool_name" == "analyze_copilot_debug_log.sh" ]]; then
        shift
        exec bash "$REPO_ROOT/tools/analyze_copilot_debug_log/run.sh" "$@"
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-}"
PYTHON_VERSION_FILE="$REPO_ROOT/.python-version"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
