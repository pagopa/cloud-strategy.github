#!/usr/bin/env bash
#
# Purpose: Run the local home AI resource sync planner and apply tool.
# Usage examples:
#   ./.github/scripts/sync_home_ai_resources.sh plan --targets codex,vscode
#   ./.github/scripts/sync_home_ai_resources.sh apply --targets codex --create-missing-dirs

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" sync_home_ai_resources "$@"
