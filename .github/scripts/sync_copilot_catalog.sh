#!/usr/bin/env bash
#
# Purpose: Run the Copilot catalog sync planner and apply tool.
# Usage examples:
#   ./.github/scripts/sync_copilot_catalog.sh plan --target-repo ../consumer-repo
#   ./.github/scripts/sync_copilot_catalog.sh apply --target-repo ../consumer-repo --allow-dirty-target

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" sync_copilot_catalog "$@"
