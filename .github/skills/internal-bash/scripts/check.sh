#!/usr/bin/env bash
# Static Bash and POSIX sh checks; never executes the checked files.
set -uo pipefail

script_path="${BASH_SOURCE[0]}"
if [[ "$script_path" == */* ]]; then
  script_dir="$(cd -- "${script_path%/*}" && pwd)"
else
  script_dir="$(pwd)"
fi
max_lines=100
max_line_chars=500
dialect_override=""
self_test=false
files=()
dialects=()

usage() {
  printf '%s\n' \
    'usage: check.sh [--dialect bash|sh] FILE [FILE ...]' \
    '       check.sh --self-test' >&2
}

log_error() {
  printf '❌ error · %s\n' "$*" >&2
}

print_bounded() {
  local text="$1" line count=0
  [[ -n "$text" ]] || return 0
  while IFS= read -r line; do
    count=$((count + 1))
    if [[ "$count" -le "$max_lines" ]]; then
      if [[ "${#line}" -gt "$max_line_chars" ]]; then
        line="${line:0:$max_line_chars} … omitted $((${#line} - max_line_chars)) characters"
      fi
      printf '  %s\n' "$line"
    fi
  done <<<"$text"
  if [[ "$count" -gt "$max_lines" ]]; then
    printf '  … omitted %s lines\n' "$((count - max_lines))"
  fi
}

require_shellcheck() {
  if ! command -v shellcheck >/dev/null 2>&1; then
    log_error 'required shellcheck is missing; install it with the system package manager, for example: brew install shellcheck'
    return 2
  fi
  local line version="unknown"
  while IFS= read -r line; do
    case "$line" in
      version:*) version="${line#version: }" ;;
    esac
  done <<<"$(shellcheck --version 2>/dev/null)"
  printf 'shellcheck version: %s\n' "$version"
}

detect_dialect() {
  local file="$1" first="" interpreter program word index=1
  local -a words=()
  if [[ -n "$dialect_override" ]]; then
    printf '%s\n' "$dialect_override"
    return 0
  fi
  IFS= read -r first <"$file" || true
  if [[ "$first" != '#!'* ]]; then
    log_error "no shebang in $file; pass --dialect bash|sh"
    return 2
  fi
  interpreter="${first#\#!}"
  read -r -a words <<<"$interpreter"
  program="${words[0]:-}"
  if [[ "${program##*/}" == env ]]; then
    program=""
    while [[ "$index" -lt "${#words[@]}" ]]; do
      word="${words[$index]}"
      index=$((index + 1))
      case "$word" in
        -* | *=*) continue ;;
      esac
      program="$word"
      break
    done
  fi
  case "${program##*/}" in
    bash) printf 'bash\n' ;;
    sh | dash) printf 'sh\n' ;;
    *)
      log_error "unsupported interpreter '$first' in $file"
      return 2
      ;;
  esac
}

check_file() {
  local file="$1" dialect="$2" syntax_tool output rc failed=false
  [[ "$file" != -* ]] || file="./$file"

  if [[ "$dialect" == bash ]]; then
    syntax_tool='bash'
  elif command -v dash >/dev/null 2>&1; then
    syntax_tool='dash'
  else
    syntax_tool='sh'
    printf '⚠️ limited evidence · sh -n ran without dash · %s\n' "$file"
  fi
  if ! command -v "$syntax_tool" >/dev/null 2>&1; then
    log_error "required interpreter $syntax_tool is missing for $file"
    return 2
  fi

  output="$("$syntax_tool" -n "$file" 2>&1)"
  rc=$?
  if [[ "$rc" -ne 0 ]]; then
    failed=true
    print_bounded "$output"
  fi

  output="$(shellcheck -s "$dialect" "$file" 2>&1)"
  rc=$?
  case "$rc" in
    0) ;;
    1)
      failed=true
      print_bounded "$output"
      ;;
    *)
      log_error "shellcheck exited with status $rc for $file"
      return 2
      ;;
  esac

  if [[ "$failed" == true ]]; then
    printf '❌ failed · %s · %s\n' "$dialect" "$file"
    return 1
  fi
  printf '✅ passed · %s · %s\n' "$dialect" "$file"
}

run_checks() {
  local index rc passed=0 failed=0
  for ((index = 0; index < ${#files[@]}; index++)); do
    check_file "${files[$index]}" "${dialects[$index]}"
    rc=$?
    case "$rc" in
      0) passed=$((passed + 1)) ;;
      1) failed=$((failed + 1)) ;;
      *) return 2 ;;
    esac
  done
  printf 'summary: passed=%s failed=%s\n' "$passed" "$failed"
  [[ "$failed" -eq 0 ]] || return 1
}

resolve_inputs() {
  local file dialect
  dialects=()
  for file in "${files[@]}"; do
    if [[ ! -f "$file" ]]; then
      log_error "input file not found: $file"
      return 2
    fi
    dialect="$(detect_dialect "$file")" || return 2
    dialects+=("$dialect")
  done
}

expect_status() {
  local expected="$1" rc
  shift
  dialect_override=""
  if [[ "$1" == --dialect ]]; then
    dialect_override="$2"
    shift 2
  fi
  files=("$@")
  resolve_inputs >/dev/null && run_checks >/dev/null
  rc=$?
  if [[ "$rc" -ne "$expected" ]]; then
    log_error "self-test expected status $expected for $*, got $rc"
    return 2
  fi
}

self_test() {
  local fixtures="${script_dir}/../fixtures"
  expect_status 0 "$fixtures/valid/tool.bash" "$fixtures/valid/helper.sh" || return 2
  expect_status 0 --dialect sh "$fixtures/valid/sourced-helper.sh" || return 2
  expect_status 1 "$fixtures/invalid/bash-in-sh.sh" || return 2
  expect_status 1 "$fixtures/invalid/unquoted.bash" || return 2
  expect_status 1 "$fixtures/invalid/syntax-error.bash" || return 2
  printf 'Bash self-test passed\n'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --self-test)
      self_test=true
      shift
      ;;
    --dialect)
      if [[ $# -lt 2 ]]; then
        log_error '--dialect requires bash or sh'
        usage
        exit 2
      fi
      case "$2" in
        bash | sh) dialect_override="$2" ;;
        *)
          log_error "unsupported dialect '$2'; use bash or sh"
          usage
          exit 2
          ;;
      esac
      shift 2
      ;;
    --help)
      usage
      exit 0
      ;;
    --)
      shift
      files+=("$@")
      break
      ;;
    -*)
      log_error "unknown option: $1"
      usage
      exit 2
      ;;
    *)
      files+=("$1")
      shift
      ;;
  esac
done

if [[ "$self_test" == true ]]; then
  if [[ ${#files[@]} -gt 0 || -n "$dialect_override" ]]; then
    usage
    exit 2
  fi
  require_shellcheck >/dev/null || exit 2
  self_test
  exit $?
fi

if [[ ${#files[@]} -eq 0 ]]; then
  log_error 'at least one input file is required'
  usage
  exit 2
fi

require_shellcheck || exit 2
resolve_inputs || exit 2
run_checks
exit $?
