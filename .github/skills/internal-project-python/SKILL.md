---
name: internal-project-python
description: Create or modify Python application components with clear separation of concerns, async/framework judgment, and deterministic pytest coverage. Use when building Python services, FastAPI/Flask apps, Python libraries, module scaffolding, or service layers.
---

# Python Project Skill

## When to use
- Services, use cases, adapters, and modules in Python applications.
- Refactoring or extending existing Python application components.
- Non-script Python code that contains business behavior.

## Boundary with internal-script-python
- **This skill**: application components inside a structured project with package layout (services, use cases, adapters).
- **internal-script-python**: standalone scripts (`scripts/`, CLI tools, one-off automation).

## Mandatory rules
- Keep business logic separated from I/O and infrastructure concerns.
- Keep module boundaries clear: business rules in one place, external integrations in another.
- Use clear, domain-relevant naming in classes, methods, and errors.
- Prefer early return and guard clauses.
- Keep code explicit and readability-first.
- Use type hints on public APIs and keep data contracts explicit.
- Choose async only when the workload is I/O-bound and the surrounding stack supports it cleanly.
- Add unit tests for testable logic.

## Minimal module example
```python
"""Purpose: Resolve account status based on domain rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("account id is required")


def resolve_account_state(account_id: AccountId, is_locked: bool) -> str:
    if is_locked:
        return "locked"
    return f"active:{account_id.value}"
```

## Testing
- Use `pytest`. Keep tests deterministic and isolated.
- BDD-like names: `given_when_then` style.
- Prefer fixtures, parameterization, and mocking only when they reduce duplication or isolate real external boundaries.
- Use coverage reports to close meaningful behavioral gaps, not as a blanket 100% doctrine.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Minimal test example
```python
import pytest

def test_given_blank_account_id_when_creating_then_raises_value_error() -> None:
    with pytest.raises(ValueError):
        AccountId(" ")
```

## Architecture and framework guidance
- Follow the repository's existing framework before introducing FastAPI, Flask, Django, or a new dependency stack.
- Keep request/transport models, domain logic, and persistence concerns in separate modules.
- Use dataclasses or typed DTOs for internal contracts, and boundary-validation models where the framework already expects them.
- Keep async flows end-to-end; do not mix blocking libraries into async request paths without an explicit bridge.

## Test-shape guidance
- Use parameterized tests for behavior that varies across a small, explicit input matrix.
- Mock network, filesystem, database, or queue boundaries; do not mock internal business logic seams by default.
- Use property-based testing only when the input space is large enough to justify it.
- Prefer targeted coverage growth on changed code and risk-heavy branches over chasing untouched lines.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Business logic mixed with I/O (DB calls, HTTP) | Untestable, hard to refactor | Extract pure logic into service/domain modules |
| Mutable default arguments (`def f(items=[])`) | Shared state between calls — classic Python gotcha | Use `None` default + create inside function |
| Bare `except:` or `except Exception:` | Swallows `KeyboardInterrupt`, `SystemExit` | Catch specific exceptions |
| No type hints on public API | Hard to understand contracts, no static analysis | Add type hints on function signatures |
| Tests that depend on execution order | Fragile test suite, non-deterministic failures | Each test must be self-contained |
| Forcing async into CPU-bound or simple flows | Adds complexity without throughput benefit | Keep it synchronous unless I/O concurrency is the real bottleneck |
| Mocking internal implementation details | Makes tests brittle and hides real regressions | Mock only true external boundaries |
| Treating line coverage as the goal | Inflates test volume without improving defect detection | Target coverage around changed behavior and risky paths |
| God classes with 10+ methods | Hard to test, hard to reason about | Split by responsibility into focused classes |

## Cross-references
- **internal-script-python** (`.github/skills/internal-script-python/SKILL.md`): for standalone scripts.
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for reviewing Python code (see `.github/skills/internal-code-review/references/anti-patterns-python.md`).
- **internal-docker** (`.github/skills/internal-docker/SKILL.md`): for containerizing Python apps.

## Validation
- `python -m compileall <paths>` (syntax check)
- `pytest tests/` (run tests)
- Lint with project's configured linter.
