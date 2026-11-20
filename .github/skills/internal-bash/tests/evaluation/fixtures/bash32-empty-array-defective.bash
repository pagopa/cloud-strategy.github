#!/usr/bin/env bash
set -euo pipefail

print_args() {
  local -a extra=()
  printf 'arg: %s\n' "${extra[@]}"
}

print_args
