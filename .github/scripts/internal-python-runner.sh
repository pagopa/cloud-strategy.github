#!/usr/bin/env bash
#
# Purpose: Bootstrap a local virtual environment for a Python entrypoint and run it consistently.
# Usage examples:
#   ./.github/scripts/internal-python-runner.sh ./.github/scripts/validate-copilot-customizations.py --scope root
#   PYTHON_BIN=python3.12 ./.github/scripts/internal-python-runner.sh ./scripts/tool.py --help

set -euo pipefail

log_info() {
  printf '%s\n' "ℹ️  $*" >&2
}

log_error() {
  printf '%s\n' "❌ $*" >&2
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log_error "Missing required command: $1"
    exit 1
  fi
}

if [[ $# -lt 1 ]]; then
  log_error "Usage: $0 <python-entrypoint> [args ...]"
  exit 1
fi

ENTRYPOINT_INPUT="$1"
shift

if [[ "$ENTRYPOINT_INPUT" = /* ]]; then
  ENTRYPOINT_PATH="$ENTRYPOINT_INPUT"
else
  ENTRYPOINT_PATH="$(cd "$(dirname "$ENTRYPOINT_INPUT")" && pwd)/$(basename "$ENTRYPOINT_INPUT")"
fi

if [[ ! -f "$ENTRYPOINT_PATH" ]]; then
  log_error "Python entrypoint not found: $ENTRYPOINT_PATH"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$ENTRYPOINT_PATH")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_STAMP="$VENV_DIR/.requirements.sha256"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -d "$VENV_DIR" ]]; then
  require_command "$PYTHON_BIN"
  log_info "Creating local virtual environment in $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

if [[ -f "$REQUIREMENTS_FILE" ]]; then
  require_command shasum
  current_requirements_hash="$(shasum -a 256 "$REQUIREMENTS_FILE" | awk '{print $1}')"
  installed_requirements_hash=""
  if [[ -f "$REQUIREMENTS_STAMP" ]]; then
    installed_requirements_hash="$(<"$REQUIREMENTS_STAMP")"
  fi

  if [[ "$current_requirements_hash" != "$installed_requirements_hash" ]]; then
    if [[ ! -x "$VENV_DIR/bin/pip" ]]; then
      log_error "Virtual environment pip not found: $VENV_DIR/bin/pip"
      exit 1
    fi

    log_info "Installing local Python dependencies from $REQUIREMENTS_FILE"
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
    printf '%s\n' "$current_requirements_hash" > "$REQUIREMENTS_STAMP"
  fi
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  log_error "Virtual environment python not found: $VENV_DIR/bin/python"
  exit 1
fi

exec "$VENV_DIR/bin/python" "$ENTRYPOINT_PATH" "$@"
