#!/bin/bash
set -u

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
required_version="checkmake version 0.3.2"
max_findings=100

usage() {
  printf 'usage: %s [--self-test | FILE [FILE ...]]\n' "$(basename "$0")" >&2
}

require_checkmake() {
  if ! command -v checkmake >/dev/null 2>&1; then
    printf 'error: required %s is missing; install with: go install github.com/checkmake/checkmake/cmd/checkmake@v0.3.2\n' \
      "$required_version" >&2
    return 2
  fi

  local version_output
  version_output="$(checkmake --version 2>&1)"
  local detected_version=""
  if [[ "$version_output" =~ ^checkmake([[:space:]]+version)?[[:space:]]+([^[:space:]]+) ]]; then
    detected_version="${BASH_REMATCH[2]}"
  fi
  if [[ "$detected_version" != "0.3.2" ]]; then
    printf 'error: required %s, found: %s\n' "$required_version" "$version_output" >&2
    printf 'install with: go install github.com/checkmake/checkmake/cmd/checkmake@v0.3.2\n' >&2
    return 2
  fi
}

validate_files() {
  local file
  for file in "$@"; do
    if [[ ! -f "$file" ]]; then
      printf 'error: input file not found: %s\n' "$file" >&2
      return 2
    fi
  done
}

run_checker() {
  local output_file rc
  output_file="$(mktemp "${TMPDIR:-/tmp}/internal-makefile.XXXXXX")" || {
    printf 'error: unable to create temporary output file\n' >&2
    return 2
  }

  checkmake \
    --config "${script_dir}/checkmake.ini" \
    --output text \
    "$@" >"$output_file" 2>&1
  rc=$?
  sed -n "1,${max_findings}p" "$output_file"
  rm -f "$output_file"

  case "$rc" in
    0) return 0 ;;
    1) return 1 ;;
    *)
      printf 'error: checkmake exited with status %s\n' "$rc" >&2
      return 2
      ;;
  esac
}

self_test() {
  local valid invalid rc
  valid="${script_dir}/../fixtures/valid/Makefile"
  invalid="${script_dir}/../fixtures/invalid/missing-phony.mk"

  run_checker "$valid"
  rc=$?
  if [[ "$rc" -ne 0 ]]; then
    printf 'error: Makefile self-test valid fixture returned %s\n' "$rc" >&2
    return 2
  fi

  run_checker "$invalid"
  rc=$?
  if [[ "$rc" -ne 1 ]]; then
    printf 'error: Makefile self-test invalid fixture returned %s\n' "$rc" >&2
    return 2
  fi

  printf 'Makefile self-test passed\n'
  return 0
}

if [[ "${1:-}" == "--self-test" ]]; then
  if [[ "$#" -ne 1 ]]; then
    usage
    exit 2
  fi
  require_checkmake || exit $?
  self_test
  exit $?
fi

if [[ "$#" -eq 0 ]]; then
  printf 'error: at least one input file is required\n' >&2
  usage
  exit 2
fi

require_checkmake || exit $?
validate_files "$@" || exit $?
run_checker "$@"
exit $?
