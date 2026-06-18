#!/usr/bin/env bash
#
# Purpose: Validate a critical-master output against the output contract.
# Usage examples:
#   ./.github/scripts/validate_critical_output.sh --file tests/fixtures/critical_output_good.md

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" validate_critical_output "$@"
