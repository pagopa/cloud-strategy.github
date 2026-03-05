# Code Review Instructions

## Primary checks
1. Security and least privilege.
2. No hardcoded secrets or credentials.
3. Consistency with repository naming and structure conventions.
4. Test coverage for testable logic.
5. Documentation updates when behavior changes (exclude `README.md` unless explicitly requested).
6. Per-language anti-pattern detection (see language-specific sections below).

## Review output format
- `Critical`: must-fix issues (security flaws, correctness bugs, data loss risk)
- `Major`: high-risk improvements (mandatory rule violations, maintainability risks)
- `Minor`: optional improvements (technical debt, clarity)
- `Nit`: style and cosmetic issues (naming, formatting, convention consistency)
- `Notes`: assumptions and follow-ups

## Severity escalation
- Any single anti-pattern repeated 3+ times in the same diff escalates one severity level.
- Any deviation from the matching `instructions/*.instructions.md` file is at minimum a `Nit`.

## Focus by area
- Terraform: drift risk, lifecycle safety, variable typing, plan readability.
- Workflows: SHA pinning, minimal permissions, environment protection.
- Scripts: input validation, early returns, readable control flow, English logs.

## Python-specific checks
Flag the following when reviewing `*.py` files:
- `Critical`: `eval()`/`exec()` on untrusted input, hardcoded secrets, `pickle.load()` on untrusted data.
- `Major`: bare `except:` without re-raise or logging, mutable default arguments, `os.system()` or `subprocess` with `shell=True`, missing type hints on public functions, functions longer than 40 lines, `print()` instead of `logging` in application code.
- `Minor`: unused imports, hardcoded file paths, missing docstrings on public functions, `noqa`/`type: ignore` without justification, mixed `str.format()` and f-strings, dead code.
- `Nit`: line length > 120, unsorted imports, inconsistent quote style, missing trailing newline.

## Bash-specific checks
Flag the following when reviewing `*.sh` files:
- `Critical`: hardcoded secrets, `eval` on user input, world-writable temp files without `mktemp`.
- `Major`: missing `set -euo pipefail`, unquoted variables outside `[[ ]]`, `cd` without error handling, missing `local` in functions, `#!/bin/sh` instead of `#!/usr/bin/env bash`, missing cleanup trap for temp files.
- `Minor`: `echo` instead of emoji logs (`ℹ️ ✅ ⚠️ ❌`), hardcoded paths, missing purpose header, `grep | awk` where single `awk` suffices, missing `command -v` checks, non-English log messages.
- `Nit`: `[ ]` instead of `[[ ]]`, backticks instead of `$()`, inconsistent indentation, missing trailing newline.

## Terraform-specific checks
Flag the following when reviewing `*.tf` files:
- `Critical`: hardcoded secrets in `.tf` files, overly broad IAM `"Action": "*"` or `"Resource": "*"`, backend with no state locking.
- `Major`: `count` where `for_each` is appropriate, missing `description` or `type` on variables, hardcoded resource IDs/ARNs, missing `prevent_destroy` on critical resources, unpinned provider versions, `ignore_changes` without documented rationale, missing tags.
- `Minor`: unused variables or outputs, missing `description` on outputs, inconsistent formatting (`terraform fmt`), inline policy JSON instead of data source, missing `create_before_destroy`.
- `Nit`: non-`snake_case` resource names, inconsistent argument ordering, `//` comments instead of `#`, missing blank lines between blocks.
