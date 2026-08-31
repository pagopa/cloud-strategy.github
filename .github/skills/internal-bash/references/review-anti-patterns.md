# Shell Review Anti-Patterns

Scope: embedded shell, sourced helpers, and non-operator shell fragments.

## Controlling review question

### Declared dialect

Identify the declared interpreter, execution environment, and POSIX baseline
before classifying a finding. A Bash extension under a POSIX `sh` shebang is a
major dialect mismatch. Do not recommend Bash syntax to a POSIX `sh` target.

## Critical

| ID | Anti-pattern | Why |
| --- | --- | --- |
| SH-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| SH-C02 | `eval` on user-controlled input | Arbitrary command execution |
| SH-C03 | World-writable temp files without `mktemp` | Race condition or symlink attack |

## Major

| ID | Anti-pattern | Why |
| --- | --- | --- |
| SH-M01 | Required status or error handling is omitted without a dialect-appropriate compatibility reason | Unchecked failures can corrupt behavior |
| SH-M02 | Unquoted variable expansion outside a safe, dialect-appropriate context | Word splitting and globbing bugs |
| SH-M03 | `cd` without an immediate failure exit | Silent directory change failure |
| SH-M04 | Bash `local` is used outside `Dialect: Bash` | POSIX `sh` cannot rely on the extension |
| SH-M05 | Bash-specific syntax under a POSIX shell shebang | The declared interpreter cannot reliably execute the script |
| SH-M06 | Missing cleanup trap for temporary files | Resource leak |
| SH-M07 | Function mixes parsing, orchestration, and mutation | Coupled responsibilities make failure handling and safe testing difficult |
| SH-M08 | Missing `pipefail` under `Dialect: Bash` or an explicit POSIX.1-2024 baseline | Pipeline failures may be hidden |

## Minor

| ID | Anti-pattern | Why |
| --- | --- | --- |
| SH-m01 | `echo` used where portable formatting or escape handling matters | Output can vary between shells and inputs |
| SH-m02 | Hardcoded paths such as `/usr/local/bin/tool` | Portability concern |
| SH-m03 | Operator-facing script lacks purpose or usage context | Operators cannot discover the entrypoint contract locally |
| SH-m04 | A `grep`-to-`awk` pipeline where one `awk` suffices | Unnecessary pipe |
| SH-m05 | Missing `command -v` check before using external tools | Fails confusingly if a tool is missing |
| SH-m06 | Non-English log messages or comments | Language policy violation |
| SH-m07 | A non-obvious function has no header comment | Callers cannot tell which globals, arguments, and outputs the helper depends on |

## Nit

| ID | Anti-pattern | Why |
| --- | --- | --- |
| SH-N01 | Bash `[ ]` use where `[[ ]]` would improve a Bash-only expression | Bash readability or word-splitting concern; not a POSIX `sh` finding |
| SH-N02 | Backticks `` `cmd` `` instead of `$(cmd)` | Readability and nesting |
| SH-N03 | Missing blank line between function definitions | Visual structure |
| SH-N04 | Inconsistent indentation | Style consistency |
| SH-N05 | Missing trailing newline at end of file | POSIX convention |

## Safe examples

```bash
# Bash branch: arrays and local are deliberate.
#!/usr/bin/env bash
set -euo pipefail

process_directory() {
  local base_dir="${1:?Missing base directory}"
  local name="${2:?Missing name}"
  cd -- "$base_dir" || {
    printf '❌ Failed to enter %s\n' "$base_dir" >&2
    return 1
  }
  printf 'ℹ️ Processing %s\n' "$name"
}
```

```sh
# POSIX sh branch: scalar variables and [ ] are deliberate.
#!/bin/sh
set -eu

process_file() {
  name=${1:?Missing name}
  if [ -z "$name" ]; then
    printf '%s\n' '❌ Missing name' >&2
    return 1
  fi
  printf 'ℹ️ Processing %s\n' "$name"
}
```
