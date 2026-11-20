#!/usr/bin/env bash
set -euo pipefail

count_logs() {
  local dir="${1:?Missing directory}"
  local count=0
  for file in $(ls "$dir"); do
    count=$((count + 1))
    printf 'log: %s\n' "$file"
  done
  printf '%s\n' "$count"
}
