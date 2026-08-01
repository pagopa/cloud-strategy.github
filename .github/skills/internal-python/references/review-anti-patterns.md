# Python Anti-Patterns

Baseline owner: `internal-python`

Use these findings when repository evidence shows a security, correctness,
maintainability, or declared-contract defect. Do not turn a tool-owned style
diagnostic into a manual review finding.

## Security and correctness

| ID | Anti-pattern | Why |
| --- | --- | --- |
| PY-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| PY-C02 | `eval()` or `exec()` on untrusted input | Arbitrary code execution |
| PY-C03 | `pickle.load()` / `pickle.loads()` on untrusted data | Deserialization attack |
| PY-M01 | Bare `except:` or broad `except Exception` without handling, logging, or re-raise | Can swallow control-flow or ordinary application failures silently |
| PY-M02 | Mutable default arguments (`def f(items=[])`) | Shared state across calls |
| PY-M03 | `os.system()` or `subprocess` with `shell=True` | Shell injection risk |
| PY-M04 | Missing type hints on public function signatures | Reduces readability and tooling support |
| PY-M07 | `print()` instead of `logging` in application or library code | Removes useful log-level control |
| PY-M10 | `rich`, emoji, tables, or panels outside human-facing CLI/reporting boundaries | Mixes terminal UI with reusable logic or machine-readable output |

## Contract and maintenance

| ID | Anti-pattern | Why |
| --- | --- | --- |
| PY-M08 | Missing focused tests for new or changed behavior | Leaves the changed contract without regression coverage |
| PY-M09 | Python tests outside repository-root `tests/` or without paths that make the covered owner or checked behavior obvious | Breaks test discoverability and ownership mapping |
| PY-m01 | Unused imports | Dead code noise |
| PY-m02 | Hardcoded file paths or URLs | Portability and configuration concern |
| PY-m04 | `noqa` or `type: ignore` without inline justification | Hides real issues |
| PY-m06 | Dead code, unreachable branches, or commented-out blocks | Maintenance burden |

## Formatter and linter boundary

Defer line length, quote style, import order, trailing newline, ambiguous-name,
and blank-line diagnostics to the repository's configured formatter and linter.
Report them here only when repository evidence proves a behavioral or contract
defect beyond the tool diagnostic.

Report readability or complexity only when repository evidence shows a
behavioral, maintainability, or declared-contract defect.

## Examples

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
    logger.warning("Fetch failed: %s", exc)
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
