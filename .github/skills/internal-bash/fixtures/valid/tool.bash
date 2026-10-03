#!/usr/bin/env bash
set -euo pipefail

main() {
  local name="${1:-world}"
  local -a greeting=(printf '%s\n')
  "${greeting[@]}" "Hello, ${name}"
}

main "$@"
