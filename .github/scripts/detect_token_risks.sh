#!/usr/bin/env bash
#
# Purpose: Run token-risk analysis for Copilot governance assets.
# Usage examples:
#   ./.github/scripts/detect_token_risks.sh --root .

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" detect_token_risks "$@"
