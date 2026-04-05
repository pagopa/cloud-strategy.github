#!/usr/bin/env bash
#
# Purpose: Run the Copilot usage reporting helper through its local virtual environment.
# Usage examples:
#   ./.github/scripts/report-copilot-usage.sh --input telemetry.jsonl
#   ./.github/scripts/report-copilot-usage.sh --input telemetry.json --markdown-out usage-report.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec bash "$SCRIPT_DIR/internal-python-runner.sh" "$SCRIPT_DIR/report-copilot-usage.py" "$@"
