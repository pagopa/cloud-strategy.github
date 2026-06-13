#!/usr/bin/env bash
#
# Purpose: Run the local GitHub catalog validation workflow simulation from the repository root.
# Usage examples:
#   bash ./github_catalog_validation.sh
#   bash ./github_catalog_validation.sh --skip-token-risks
#   bash ./github_catalog_validation.sh --token-risks-only

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec bash "$REPO_ROOT/.github/scripts/github_catalog_validation.sh" "$@"
