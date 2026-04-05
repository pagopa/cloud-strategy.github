#!/usr/bin/env bash
#
# Purpose: Run the Copilot customization validator through its local virtual environment.
# Usage examples:
#   ./.github/scripts/validate-copilot-customizations.sh --scope root --mode strict
#   ./.github/scripts/validate-copilot-customizations.sh --report json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec bash "$SCRIPT_DIR/internal-python-runner.sh" "$SCRIPT_DIR/validate-copilot-customizations.py" "$@"
