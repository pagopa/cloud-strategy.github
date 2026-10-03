#!/bin/sh
set -eu

print_entries() {
  while IFS= read -r entry; do
    printf '%s\n' "$entry"
  done <"${1:?Missing list file}"
}
