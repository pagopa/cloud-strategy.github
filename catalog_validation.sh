#!/usr/bin/env bash
#
# Purpose: Run the local catalog-validation workflow simulation from the repository root.
# Usage examples:
#   ./catalog_validation.sh
#   ./catalog_validation.sh --skip-token-risks
#   ./catalog_validation.sh --token-risks-only

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$REPO_ROOT/.github/scripts/catalog_validation.sh" "$@"
