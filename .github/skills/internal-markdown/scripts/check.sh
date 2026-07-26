#!/bin/bash
set -u

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
required_version="markdownlint-cli2 v0.22.1"
max_findings=100
max_files=100

usage() {
  printf 'usage: %s [--self-test | FILE [FILE ...]]\n' "$(basename "$0")" >&2
}

require_markdownlint() {
  if ! command -v markdownlint-cli2 >/dev/null 2>&1; then
    printf 'error: required %s is missing; install with: npm install -g markdownlint-cli2@0.22.1\n' \
      "$required_version" >&2
    return 2
  fi

  local version_output
  version_output="$(markdownlint-cli2 --version 2>&1)"
  if [[ "$version_output" != *"$required_version"* ]]; then
    printf 'error: required %s, found: %s\n' "$required_version" "$version_output" >&2
    printf 'install with: npm install -g markdownlint-cli2@0.22.1\n' >&2
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

run_file() {
  local file="$1"
  local output_file rc
  output_file="$(mktemp "${TMPDIR:-/tmp}/internal-markdown.XXXXXX")" || {
    printf 'error: unable to create temporary output file\n' >&2
    return 2
  }

  markdownlint-cli2 \
    --config "${script_dir}/markdownlint-cli2.jsonc" \
    - < "$file" >"$output_file" 2>&1
  rc=$?
  sed -n "1,${max_findings}p" "$output_file"
  rm -f "$output_file"

  case "$rc" in
    0) return 0 ;;
    1) return 1 ;;
    *)
      printf 'error: markdownlint-cli2 exited with status %s for %s\n' "$rc" "$file" >&2
      return 2
      ;;
  esac
}

run_files() {
  local finding=0 rc file_count=0
  local file
  for file in "$@"; do
    file_count=$((file_count + 1))
    if [[ "$file_count" -gt "$max_files" ]]; then
      break
    fi
    run_file "$file"
    rc=$?
    case "$rc" in
      0) ;;
      1) finding=1 ;;
      *) return 2 ;;
    esac
  done
  return "$finding"
}

self_test() {
  local valid invalid rc
  valid="${script_dir}/../fixtures/valid/document.md"
  invalid="${script_dir}/../fixtures/invalid/broken-references.md"

  run_files "$valid"
  rc=$?
  if [[ "$rc" -ne 0 ]]; then
    printf 'error: Markdown self-test valid fixture returned %s\n' "$rc" >&2
    return 2
  fi

  run_files "$invalid"
  rc=$?
  if [[ "$rc" -ne 1 ]]; then
    printf 'error: Markdown self-test invalid fixture returned %s\n' "$rc" >&2
    return 2
  fi

  printf 'Markdown self-test passed\n'
  return 0
}

if [[ "${1:-}" == "--self-test" ]]; then
  if [[ "$#" -ne 1 ]]; then
    usage
    exit 2
  fi
  require_markdownlint || exit $?
  self_test
  exit $?
fi

if [[ "$#" -eq 0 ]]; then
  printf 'error: at least one input file is required\n' >&2
  usage
  exit 2
fi

require_markdownlint || exit $?
validate_files "$@" || exit $?
run_files "$@"
exit $?
