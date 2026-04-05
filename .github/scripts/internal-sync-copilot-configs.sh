#!/usr/bin/env bash
#
# Purpose: Run the Copilot sync planner and apply workflow through its local virtual environment.
# Usage examples:
#   ./.github/scripts/internal-sync-copilot-configs.sh --target /path/to/repo
#   ./.github/scripts/internal-sync-copilot-configs.sh --target /path/to/repo --mode apply

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec bash "$SCRIPT_DIR/internal-python-runner.sh" "$SCRIPT_DIR/internal-sync-copilot-configs.py" "$@"
