#!/bin/sh
set -eu

name=${1:-world}
if [ -n "$name" ]; then
  printf 'Hello, %s\n' "$name"
fi
