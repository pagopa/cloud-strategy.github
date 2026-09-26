# Shell Review Anti-Patterns

Scope: every shell file or fragment reviewed through `internal-bash`,
including standalone scripts reviewed through `internal-bash-script`. Operator
entrypoint findings live in that skill's common-mistakes reference.

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
| SH-C04 | Command text from an untrusted source runs through `sh -c` or `bash -c`; fixed command text with separately passed arguments is not a finding, and `eval` stays SH-C02 | Arbitrary command execution |
| SH-C05 | Downloaded content runs without verification against a trusted digest or signature; HTTPS alone or a digest fetched from the same source is not verification | Supply-chain code execution |

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
| SH-M09 | `read` without `-r` or `IFS=` where backslashes or surrounding whitespace must be preserved; intentional field splitting is not a finding | Input is silently altered |
| SH-M10 | Filenames pass through word splitting or globbing of a command substitution, such as `for f in $(ls)`; fix with a quoted glob, `find -exec`, or a NUL-delimited reader the dialect supports | Names with spaces or glob characters break |
| SH-M11 | A failure is suppressed because the function runs in an `if`, `&&`, `\|\|`, or `!` context where `set -e` does not apply; explicit status handling is not a finding | The caller continues after a failed step |
| SH-M12 | Under a declared `Compatibility target: Bash 3.2`, reachable use of Bash 4+ features or an empty-array expansion under `set -u`; ordinary arrays are valid | The script fails on macOS `/bin/bash` |

## Minor

| ID | Anti-pattern | Why |
| --- | --- | --- |
| SH-m01 | `echo` used where portable formatting or escape handling matters | Output can vary between shells and inputs |
| SH-m02 | Hardcoded paths such as `/usr/local/bin/tool` | Portability concern |
| SH-m04 | A `grep`-to-`awk` pipeline where one `awk` suffices | Unnecessary pipe |
| SH-m05 | Missing `command -v` check before using external tools | Fails confusingly if a tool is missing |
| SH-m06 | Non-English log messages or comments | Language policy violation |
| SH-m07 | A non-obvious function has no header comment | Callers cannot tell which globals, arguments, and outputs the helper depends on |
| SH-m08 | An unmatched glob is used as a literal with low impact; guard with `[ -e ]`, never prescribe Bash `nullglob` for POSIX `sh`, and raise severity when the command is destructive | The loop processes the pattern text itself |

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
#!/usr/bin/env bash
# Bash branch: arrays and local are deliberate.
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
#!/bin/sh
# POSIX sh branch: scalar variables and [ ] are deliberate.
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
