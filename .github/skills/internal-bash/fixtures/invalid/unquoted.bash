#!/usr/bin/env bash
set -euo pipefail

target_dir="${1:?Missing target directory}"
cd $target_dir
rm -rf $target_dir/cache
