#!/usr/bin/env bash
#
# Purpose: Remove a cache directory for one environment.
# Usage examples:
#   ./cache-clean.sh --env dev --dry-run
#   ./cache-clean.sh --help

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: ./cache-clean.sh --env NAME [--dry-run]'
}

main() {
  local env_name="" dry_run=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --env)
        [[ $# -ge 2 && "$2" != -* ]] || {
          printf '%s\n' '--env requires a value' >&2
          exit 1
        }
        env_name="$2"
        shift 2
        ;;
      --dry-run) dry_run=true; shift ;;
      --help) usage; exit 0 ;;
      *) usage >&2; exit 1 ;;
    esac
  done
  [[ -n "$env_name" ]] || { usage >&2; exit 1; }

  local target="${CACHE_ROOT:?CACHE_ROOT is required}/${env_name}"
  if [[ "$dry_run" == true ]]; then
    printf 'would remove %s\n' "$target"
    return 0
  fi
  rm -rf -- "$target"
}

main "$@"
