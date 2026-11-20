#!/bin/sh
set -eu

rotate_logs() {
  log_dir=${1:?Missing log directory}
  cd "$log_dir" || return 1
  for log in *.log; do
    [ -e "$log" ] || continue
    mv -- "$log" "$log.1"
  done
}
