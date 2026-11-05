#!/usr/bin/env bash
set -euo pipefail

count_logs() {
  local dir="${1:?Missing directory}"
  local count=0
  local file
  for file in "$dir"/*; do
    [[ -e "$file" ]] || continue
    count=$((count + 1))
    printf 'log: %s\n' "$file"
  done
  printf '%s\n' "$count"
}
