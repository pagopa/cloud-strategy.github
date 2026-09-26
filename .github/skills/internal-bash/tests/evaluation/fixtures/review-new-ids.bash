#!/usr/bin/env bash
set -euo pipefail

run_remote_hook() {
  local hook_cmd="${1:?Missing hook command}"
  sh -c "$hook_cmd"
}

run_fixed_hook() {
  sh -c 'printf "%s\n" "$1"' hook "${1:?Missing hook argument}"
}

install_tool() {
  curl -fsSL https://example.invalid/install.sh | sh
}

install_verified_tool() {
  local archive="${1:?Missing archive}"
  local expected_sha="${2:?Missing expected digest}"
  printf '%s  %s\n' "$expected_sha" "$archive" | shasum -a 256 -c -
}

sync_cache() {
  mkdir -p /tmp/example-cache
  cp -R ./cache/. /tmp/example-cache/
  printf 'synced\n'
}

if sync_cache; then
  printf 'cache ready\n'
fi

if ! cp -R ./cache/. /tmp/example-cache/; then
  printf 'copy failed\n' >&2
  exit 1
fi

for report in ./reports/*.txt; do
  printf 'report: %s\n' "$report"
done
