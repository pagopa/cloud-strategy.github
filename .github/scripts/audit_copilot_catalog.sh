#!/usr/bin/env bash
#
# Purpose: Run the deep Copilot catalog audit.
# Usage examples:
#   ./.github/scripts/audit_copilot_catalog.sh --root .

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" audit_copilot_catalog "$@"
