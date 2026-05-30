#!/usr/bin/env bash
#
# Purpose: Bootstrap this skill's local Python environment and run the home AI resource sync tool.
# Usage examples:
#   ./scripts/run.sh plan --targets codex,copilot,claude,opencode
#   ./scripts/run.sh apply --targets codex --create-missing-dirs

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

ensure_venv() {
  if [[ -d "$VENV_DIR" ]]; then
    return
  fi
  log_info "Creating skill-local virtual environment."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
}

install_dependencies() {
  local requirements_hash=""
  local current_hash=""

  requirements_hash="$(hash_file "$REQUIREMENTS_FILE")"
  if [[ -f "$REQUIREMENTS_HASH_FILE" ]]; then
    current_hash="$(<"$REQUIREMENTS_HASH_FILE")"
  fi

  if [[ "$requirements_hash" == "$current_hash" ]]; then
    return
  fi

  log_info "Installing locked skill dependencies."
  "$VENV_DIR/bin/pip" install --require-hashes -r "$REQUIREMENTS_FILE"
  printf '%s' "$requirements_hash" >"$REQUIREMENTS_HASH_FILE"
  log_success "Skill Python environment is ready."
}

main() {
  require_command "$PYTHON_BIN"
  ensure_venv
  install_dependencies
  exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/sync_home_ai_resources.py" "$@"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

main "$@"