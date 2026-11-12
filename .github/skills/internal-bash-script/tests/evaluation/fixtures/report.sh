#!/usr/bin/env bash
#
# Purpose: Print a line count report for a directory.
# Usage examples:
#   ./report.sh --dir src
#   ./report.sh --help

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: ./report.sh --dir PATH'
}

main() {
  local dir=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dir)
        [[ $# -ge 2 && "$2" != -* ]] || { usage >&2; exit 1; }
        dir="$2"
        shift 2
        ;;
      --help) usage; exit 0 ;;
      *) usage >&2; exit 1 ;;
    esac
  done
  [[ -n "$dir" ]] || { usage >&2; exit 1; }
  printf 'files=%s\n' "$(find "$dir" -type f | wc -l | tr -d ' ')"
}

main "$@"
