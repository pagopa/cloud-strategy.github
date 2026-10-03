#!/bin/sh
set -eu

print_entries() {
  while read entry; do
    printf '%s\n' "$entry"
  done <"${1:?Missing list file}"
}
