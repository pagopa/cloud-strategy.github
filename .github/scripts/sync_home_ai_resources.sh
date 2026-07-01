#!/usr/bin/env bash
#
# Purpose: Run the local home AI resource sync planner and apply tool.
# Usage examples:
#   ./.github/scripts/sync_home_ai_resources.sh sync --targets skills --format report
#   ./.github/scripts/sync_home_ai_resources.sh apply --targets codex --create-missing-dirs --format report

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" sync_home_ai_resources "$@"
