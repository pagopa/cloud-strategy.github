#!/usr/bin/env bash
set -euo pipefail

format="text"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --format) format="$2"; shift 2 ;;
    *) exit 1 ;;
  esac
done

if [[ "$format" == compact ]]; then
  printf 'ok=%s fail=%s\n' 3 0
else
  printf 'passed: 3\nfailed: 0\n'
fi
