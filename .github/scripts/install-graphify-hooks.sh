#!/usr/bin/env bash
#
# Purpose: install repository-owned Git hooks that keep graphify current.
# Usage examples:
#   ./.github/scripts/install-graphify-hooks.sh

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"
git config core.hooksPath .github/hooks

printf 'Installed Git hooks path: %s\n' '.github/hooks'
