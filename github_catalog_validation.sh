#!/usr/bin/env bash
#
# Purpose: Run the local GitHub catalog validation workflow simulation from the repository root.
# Usage examples:
#   ./github_catalog_validation.sh
#   ./github_catalog_validation.sh --skip-token-risks
#   ./github_catalog_validation.sh --token-risks-only

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$REPO_ROOT/.github/scripts/github_catalog_validation.sh" "$@"