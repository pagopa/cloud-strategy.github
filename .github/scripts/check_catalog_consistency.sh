#!/usr/bin/env bash
#
# Purpose: Run the fast Copilot catalog consistency checks.
# Usage examples:
#   ./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" check_catalog_consistency "$@"
