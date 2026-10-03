#!/bin/sh
set -eu

check_name() {
  local name="${1:-}"
  if [[ -z "$name" ]]; then
    return 1
  fi
}

check_name "$@"
