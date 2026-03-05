---
name: code-review
description: Exhaustive per-language anti-pattern catalogs and severity mappings for strict code reviews of Python, Bash, and Terraform.
---

# Code Review Skill

## When to use
- Perform an exhaustive, nit-level code review on Python, Bash, or Terraform files.
- Provide structured findings with per-language anti-pattern detection.
- Complement the generic `Reviewer` agent with deep language-specific checks.

## Severity levels
| Level | Meaning | Action |
|---|---|---|
| `Critical` | Security flaw, data loss risk, or correctness bug | Must fix before merge |
| `Major` | High-risk maintainability issue or deviation from mandatory rules | Should fix before merge |
| `Minor` | Improvement that reduces technical debt or improves clarity | Fix recommended |
| `Nit` | Style inconsistency, naming preference, or cosmetic issue | Fix optional but encouraged |
| `Notes` | Assumptions, open questions, or follow-up suggestions | Informational only |

## Escalation rules
- Any single anti-pattern repeated three or more times in the same diff escalates one severity level (e.g., `Nit` → `Minor`, `Minor` → `Major`).
- Any deviation from the matching `instructions/*.instructions.md` is at minimum a `Nit`.
- Any violation of `security-baseline.md` is at minimum a `Major`.

---

## Python anti-patterns

Reference: `instructions/python.instructions.md`

### Critical
| ID | Anti-pattern | Why |
|---|---|---|
| PY-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| PY-C02 | `eval()` or `exec()` on untrusted input | Arbitrary code execution |
| PY-C03 | `pickle.load()` / `pickle.loads()` on untrusted data | Deserialization attack |

### Major
| ID | Anti-pattern | Why |
|---|---|---|
| PY-M01 | Bare `except:` or `except Exception:` without re-raise or logging | Swallows errors silently |
| PY-M02 | Mutable default arguments (`def f(items=[])`) | Shared state across calls |
| PY-M03 | `os.system()` or `subprocess` with `shell=True` | Shell injection risk |
| PY-M04 | Missing type hints on public function signatures | Reduces readability and tooling support |
| PY-M05 | Function body longer than 40 lines (excluding docstring) | Complexity and testability concern |
| PY-M06 | Cyclomatic complexity > 10 per function | Hard to test and maintain |
| PY-M07 | `print()` instead of `logging` in application/library code | No log level control in production |
| PY-M08 | Missing unit tests for new public functions | Violates test coverage mandate |

### Minor
| ID | Anti-pattern | Why |
|---|---|---|
| PY-m01 | Unused imports | Dead code noise |
| PY-m02 | Hardcoded file paths or URLs | Portability and configuration concern |
| PY-m03 | Missing docstring on public functions/classes | Reduces discoverability |
| PY-m04 | `noqa` or `type: ignore` without inline justification | Hides real issues |
| PY-m05 | Mixed `str.format()` and f-strings in the same module | Style inconsistency |
| PY-m06 | Dead code (unreachable branches, commented-out blocks) | Maintenance burden |
| PY-m07 | Missing `__all__` in modules with public API | Ambiguous public surface |
| PY-m08 | Nested functions deeper than 2 levels | Readability concern |

### Nit
| ID | Anti-pattern | Why |
|---|---|---|
| PY-N01 | Line length > 120 characters | PEP8 / repo convention |
| PY-N02 | Missing trailing newline at end of file | POSIX convention |
| PY-N03 | Inconsistent quote style (single vs double) within a module | Style preference |
| PY-N04 | Import not sorted (stdlib → third-party → local) | Convention consistency |
| PY-N05 | Variable named `l`, `O`, `I` (ambiguous with digits) | Readability |
| PY-N06 | Missing empty line between logical sections | Visual structure |

### Good vs bad examples

```python
# BAD (PY-M01): bare except
try:
    result = fetch_data()
except:
    pass

# GOOD: specific exception, logged
try:
    result = fetch_data()
except requests.RequestException as exc:
    logger.warning("⚠️ Fetch failed: %s", exc)
    raise
```

```python
# BAD (PY-M02): mutable default
def add_item(name: str, items: list = []) -> list:
    items.append(name)
    return items

# GOOD: None sentinel
def add_item(name: str, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(name)
    return items
```

```python
# BAD (PY-M07): print in library code
def process(data):
    print(f"Processing {len(data)} items")

# GOOD: structured logging
import logging
logger = logging.getLogger(__name__)

def process(data: list[dict]) -> None:
    logger.info("ℹ️ Processing %d items", len(data))
```

---

## Bash anti-patterns

Reference: `instructions/bash.instructions.md`

### Critical
| ID | Anti-pattern | Why |
|---|---|---|
| SH-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| SH-C02 | `eval` on user-controlled input | Arbitrary command execution |
| SH-C03 | World-writable temp files without `mktemp` | Race condition / symlink attack |

### Major
| ID | Anti-pattern | Why |
|---|---|---|
| SH-M01 | Missing `set -euo pipefail` | Silent failures and undefined variables |
| SH-M02 | Unquoted variable expansion outside `[[ ]]` | Word splitting and globbing bugs |
| SH-M03 | `cd` without error handling (`cd dir \|\| exit 1`) | Silent directory change failure |
| SH-M04 | Missing `local` keyword for function variables | Pollutes global scope |
| SH-M05 | POSIX `#!/bin/sh` instead of `#!/usr/bin/env bash` | Repo mandates Bash |
| SH-M06 | Missing cleanup trap (`trap cleanup EXIT`) for temp files | Resource leak |
| SH-M07 | Function body longer than 30 lines | Complexity concern |

### Minor
| ID | Anti-pattern | Why |
|---|---|---|
| SH-m01 | `echo` for status messages instead of emoji logs (`ℹ️ ✅ ⚠️ ❌`) | Repo convention violation |
| SH-m02 | Hardcoded paths (e.g., `/usr/local/bin/tool`) | Portability concern |
| SH-m03 | Missing purpose header comment | Repo convention |
| SH-m04 | `grep \| awk` where a single `awk` suffices | Unnecessary pipe |
| SH-m05 | Missing `command -v` check before using external tools | Fails confusingly if tool missing |
| SH-m06 | Non-English log messages or comments | Language policy violation |

### Nit
| ID | Anti-pattern | Why |
|---|---|---|
| SH-N01 | `[ ... ]` instead of `[[ ... ]]` | Bash convention |
| SH-N02 | Backticks `` `cmd` `` instead of `$(cmd)` | Readability and nesting |
| SH-N03 | Missing blank line between function definitions | Visual structure |
| SH-N04 | Inconsistent indentation (mix of tabs and spaces) | Style consistency |
| SH-N05 | Missing trailing newline at end of file | POSIX convention |

### Good vs bad examples

```bash
# BAD (SH-M01, SH-M05): POSIX, no strict mode
#!/bin/sh
name=$1
cd /tmp
rm -rf $name

# GOOD: Bash, strict mode, safe patterns
#!/usr/bin/env bash
set -euo pipefail

local name="${1:?Missing required argument: name}"
cd /tmp || { echo "❌ Failed to cd /tmp"; exit 1; }
rm -rf "${name}"
```

```bash
# BAD (SH-M04): global variable in function
process_file() {
  result=$(cat "$1")
  count=${#result}
}

# GOOD: local variables
process_file() {
  local result
  local count
  result=$(cat "$1")
  count=${#result}
  echo "ℹ️ Processed ${count} bytes"
}
```

---

## Terraform anti-patterns

Reference: `instructions/terraform.instructions.md`

### Critical
| ID | Anti-pattern | Why |
|---|---|---|
| TF-C01 | Hardcoded secrets, access keys, or passwords in `.tf` files | Credential exposure |
| TF-C02 | Overly broad IAM policy with `"Action": "*"` or `"Resource": "*"` | Excessive privilege |
| TF-C03 | Backend configuration with no state locking | Concurrent state corruption |

### Major
| ID | Anti-pattern | Why |
|---|---|---|
| TF-M01 | `count` used where `for_each` with logical keys is appropriate | Index-based drift risk |
| TF-M02 | Missing `description` on variables | Undocumented interface |
| TF-M03 | Missing `type` constraint on variables | Unvalidated input |
| TF-M04 | Hardcoded resource IDs, ARNs, or subscription IDs | Non-portable, environment-coupled |
| TF-M05 | Missing `prevent_destroy` on critical production resources | Accidental deletion risk |
| TF-M06 | Provider version not pinned in `required_providers` | Non-deterministic plans |
| TF-M07 | `ignore_changes` without documented rationale | Hidden drift |
| TF-M08 | Missing tags on taggable resources | Governance and cost tracking gap |

### Minor
| ID | Anti-pattern | Why |
|---|---|---|
| TF-m01 | Unused variables or outputs | Dead code |
| TF-m02 | Missing `description` on outputs | Undocumented contract |
| TF-m03 | Missing `terraform fmt` (inconsistent formatting) | Style consistency |
| TF-m04 | Inline policy JSON instead of `aws_iam_policy_document` data source | Readability and validation |
| TF-m05 | Missing `create_before_destroy` on replacement-sensitive resources | Downtime risk |
| TF-m06 | Locals not grouped by domain | Organizational clarity |

### Nit
| ID | Anti-pattern | Why |
|---|---|---|
| TF-N01 | Resource name not in `snake_case` | Naming convention |
| TF-N02 | Inconsistent ordering of block arguments | Readability |
| TF-N03 | Empty `default = ""` instead of `default = null` for optional strings | Semantic clarity |
| TF-N04 | Comments with `//` instead of `#` | HCL convention |
| TF-N05 | Missing blank line between resource blocks | Visual structure |

### Good vs bad examples

```hcl
# BAD (TF-M01): count with conditional
resource "aws_iam_role" "lambda" {
  count = var.enable_lambda ? 1 : 0
  name  = "lambda-role-${count.index}"
}

# GOOD: for_each with logical key
resource "aws_iam_role" "lambda" {
  for_each = var.enable_lambda ? toset(["main"]) : toset([])
  name     = "lambda-role-${each.key}"
}
```

```hcl
# BAD (TF-M02, TF-M03): no description, no type
variable "env" {}

# GOOD: typed, described, validated
variable "env" {
  description = "Deployment environment name."
  type        = string

  validation {
    condition     = contains(["dev", "uat", "prod"], var.env)
    error_message = "env must be one of: dev, uat, prod."
  }
}
```

---

## Cross-language checks

These apply regardless of language:

| Severity | Check |
|---|---|
| `Critical` | Hardcoded secrets, tokens, passwords, or API keys |
| `Major` | Missing input validation on external inputs |
| `Major` | Missing error handling on I/O operations |
| `Minor` | Non-English comments, logs, or error messages |
| `Minor` | TODO/FIXME/HACK without linked issue or ticket |
| `Nit` | Trailing whitespace or inconsistent EOF newlines |

## Review workflow

1. **Identify languages** in the diff (auto-detect from file extensions).
2. **Load applicable checklists** from the sections above.
3. **Scan each changed file** against the relevant anti-pattern catalog.
4. **Apply escalation rules** for repeated violations.
5. **Group findings** by severity: `Critical` → `Major` → `Minor` → `Nit` → `Notes`.
6. **Include file path and line reference** for every finding.
7. **Suggest a concrete fix** or reference the "good" example for each finding.
8. **Summarize** total finding count per severity at the end.

## Validation
- Verify every finding references a real file path and line from the diff.
- Verify severity assignments match the anti-pattern catalog rules above.
- Verify escalation rules are applied for repeated violations (3+ of the same kind).
- Verify cross-language checks are applied regardless of primary language.
