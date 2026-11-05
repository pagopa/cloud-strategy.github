#!/usr/bin/env bash
set -euo pipefail

print_args() {
  local -a extra=()
  if [[ ${#extra[@]} -gt 0 ]]; then
    printf 'arg: %s\n' "${extra[@]}"
  fi
}

print_args
