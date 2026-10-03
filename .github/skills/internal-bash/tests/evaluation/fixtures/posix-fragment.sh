set -eu

prepare_workspace() {
  work_dir=$1
  cd $work_dir
  if [ -d "$work_dir/cache" ]; then
    rm -rf $work_dir/cache
  fi
}
