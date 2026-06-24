#!/usr/bin/env bash
#
# Purpose: Validate repository-owned internal skill metadata and references.
# Usage examples:
#   ./.github/scripts/validate_internal_skills.sh --root . --strict

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" validate_internal_skills "$@"
