#!/usr/bin/env bash
#
# Purpose: Run the GitHub catalog validation workflow simulation.
# Usage examples:
#   bash ./.github/scripts/github_catalog_validation.sh
#   bash ./.github/scripts/github_catalog_validation.sh --skip-token-risks

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" github_catalog_validation "$@"
