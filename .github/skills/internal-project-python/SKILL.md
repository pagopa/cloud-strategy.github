---
name: internal-project-python
description: Create or modify Python application components with clear separation of concerns, early returns, and deterministic pytest coverage. Use when building Python services, FastAPI/Flask apps, Python libraries, module scaffolding, or service layers.
---

# Python Project Skill

## When to use
- Services, use cases, adapters, and modules in Python applications.
- Refactoring or extending existing Python application components.
- Non-script Python code that contains business behavior.

## Boundary with TechAIScriptPython
- **This skill**: application components inside a structured project with package layout (services, use cases, adapters).
- **TechAIScriptPython**: standalone scripts (`scripts/`, CLI tools, one-off automation).

## Mandatory rules
- Keep business logic separated from I/O and infrastructure concerns.
- Keep module boundaries clear: business rules in one place, external integrations in another.
- Use clear, domain-relevant naming in classes, methods, and errors.
- Prefer early return and guard clauses.
- Keep code explicit and readability-first.
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
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Minimal test example
```python
import pytest

def test_given_blank_account_id_when_creating_then_raises_value_error() -> None:
    with pytest.raises(ValueError):
        AccountId(" ")
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Business logic mixed with I/O (DB calls, HTTP) | Untestable, hard to refactor | Extract pure logic into service/domain modules |
| Mutable default arguments (`def f(items=[])`) | Shared state between calls — classic Python gotcha | Use `None` default + create inside function |
| Bare `except:` or `except Exception:` | Swallows `KeyboardInterrupt`, `SystemExit` | Catch specific exceptions |
| No type hints on public API | Hard to understand contracts, no static analysis | Add type hints on function signatures |
| Tests that depend on execution order | Fragile test suite, non-deterministic failures | Each test must be self-contained |
| God classes with 10+ methods | Hard to test, hard to reason about | Split by responsibility into focused classes |

## Cross-references
- **TechAIScriptPython** (`.github/skills/tech-ai-script-python/SKILL.md`): for standalone scripts.
- **TechAICodeReview** (`.github/skills/tech-ai-code-review/SKILL.md`): for reviewing Python code (see `references/anti-patterns-python.md`).
- **TechAIDocker** (`.github/skills/tech-ai-docker/SKILL.md`): for containerizing Python apps.

## Validation
- `python -m compileall <paths>` (syntax check)
- `pytest tests/` (run tests)
- Lint with project's configured linter.
