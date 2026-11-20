#!/usr/bin/env bash
set -euo pipefail

env_name="$1"
rm -rf "$CACHE_ROOT/$env_name"
