#!/usr/bin/env bash
#
# Purpose: Bootstrap a local virtual environment for a Python entrypoint and run it consistently.
# Usage examples:
#   ./.github/scripts/internal-python-runner.sh ./.github/scripts/validate-copilot-customizations.py --scope root
#   PYTHON_BIN=python3.12 ./.github/scripts/internal-python-runner.sh ./scripts/tool.py --help

set -euo pipefail

if [[ $# -lt 1 ]]; then
  printf '%s\n' "❌ Usage: $0 <python-entrypoint> [args ...]" >&2
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
  printf '%s\n' "❌ Python entrypoint not found: $ENTRYPOINT_PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$ENTRYPOINT_PATH")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
REQUIREMENTS_STAMP="$VENV_DIR/.requirements.sha256"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -d "$VENV_DIR" ]]; then
  printf '%s\n' "ℹ️  Creating local virtual environment in $VENV_DIR" >&2
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

if [[ -f "$REQUIREMENTS_FILE" ]]; then
  current_requirements_hash="$(shasum -a 256 "$REQUIREMENTS_FILE" | awk '{print $1}')"
  installed_requirements_hash=""
  if [[ -f "$REQUIREMENTS_STAMP" ]]; then
    installed_requirements_hash="$(<"$REQUIREMENTS_STAMP")"
  fi

  if [[ "$current_requirements_hash" != "$installed_requirements_hash" ]]; then
    printf '%s\n' "ℹ️  Installing local Python dependencies from $REQUIREMENTS_FILE" >&2
    if grep -q -- "--hash=" "$REQUIREMENTS_FILE"; then
      "$VENV_DIR/bin/pip" install --require-hashes -r "$REQUIREMENTS_FILE"
    else
      "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
    fi
    printf '%s\n' "$current_requirements_hash" > "$REQUIREMENTS_STAMP"
  fi
fi

exec "$VENV_DIR/bin/python" "$ENTRYPOINT_PATH" "$@"
