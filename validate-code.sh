#!/usr/bin/env bash
#
# Purpose: Run repository static and sharded Python validation units.
# Usage examples:
#   ./validate-code.sh --list
#   ./validate-code.sh python --group repository --compact
#   ./validate-code.sh static --leaf python-lint --format ci

set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
while [[ -h "${SOURCE}" ]]; do
  SOURCE_DIR="$(cd -- "$(dirname -- "${SOURCE}")" && pwd)"
  SOURCE="$(readlink -- "${SOURCE}")"
  [[ "${SOURCE}" == /* ]] || SOURCE="${SOURCE_DIR}/${SOURCE}"
done
REPOSITORY_ROOT="$(cd -- "$(dirname -- "${SOURCE}")" && pwd)"

# Prefer the pinned toolkit venv so pytest and ruff match CI.
PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "${PYTHON_BIN}" ]]; then
  if [[ -x "${REPOSITORY_ROOT}/.github/tools/.venv/bin/python" ]]; then
    PYTHON_BIN="${REPOSITORY_ROOT}/.github/tools/.venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

cd -- "${REPOSITORY_ROOT}"
exec "${PYTHON_BIN}" -m tools.validate_code.validate_code "$@"
