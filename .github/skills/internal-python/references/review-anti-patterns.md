# Python Anti-Patterns

Baseline owner: `internal-python`

## Critical

| ID | Anti-pattern | Why |
| --- | --- | --- |
| PY-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| PY-C02 | `eval()` or `exec()` on untrusted input | Arbitrary code execution |
| PY-C03 | `pickle.load()` / `pickle.loads()` on untrusted data | Deserialization attack |

## Major

| ID | Anti-pattern | Why |
| --- | --- | --- |
| PY-M01 | Bare `except:` or broad `except Exception` without handling, logging, or re-raise | Can swallow control-flow or ordinary application failures silently |
| PY-M02 | Mutable default arguments (`def f(items=[])`) | Shared state across calls |
| PY-M03 | `os.system()` or `subprocess` with `shell=True` | Shell injection risk |
| PY-M04 | Missing type hints on public function signatures | Reduces readability and tooling support |
| PY-M07 | `print()` instead of `logging` in application/library code | No log level control in production |
| PY-M08 | Missing focused tests for new or changed behavior | Leaves the changed contract without regression coverage |
| PY-M09 | Python tests outside repository-root `tests/` or without paths that make the covered owner or checked behavior obvious | Breaks repository test discoverability and ownership mapping |
| PY-M10 | `rich`, emoji, tables, or panels outside human-facing CLI/reporting boundaries | Mixes terminal UI with importable logic or machine-readable output such as JSON |

## Minor

| ID | Anti-pattern | Why |
| --- | --- | --- |
| PY-m01 | Unused imports | Dead code noise |
| PY-m02 | Hardcoded file paths or URLs | Portability and configuration concern |
| PY-m04 | `noqa` or `type: ignore` without inline justification | Hides real issues |
| PY-m06 | Dead code (unreachable branches, commented-out blocks) | Maintenance burden |

## Formatter and linter boundary

Defer line length, quote style, import order, trailing newline, ambiguous-name,
and blank-line diagnostics to the repository's configured formatter and linter.
Report them here only when repository evidence proves a behavioral or contract
defect beyond the tool diagnostic.

Report readability or complexity only when repository evidence shows a
behavioral, maintainability, or declared-contract defect.

## Good vs bad examples

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

```python
# BAD (PY-M07): print in library code
def process(data):
    print(f"Processing {len(data)} items")

# GOOD: structured logging
import logging
logger = logging.getLogger(__name__)

def process(data: list[dict]) -> None:
    logger.info("Processing %d items", len(data))
```
