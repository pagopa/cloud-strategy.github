#!/usr/bin/env bash
#
# Purpose: Run the Copilot inventory builder.
# Usage examples:
#   ./.github/scripts/build_inventory.sh --root .

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" build_inventory "$@"
