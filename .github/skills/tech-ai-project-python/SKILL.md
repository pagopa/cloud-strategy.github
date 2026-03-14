---
name: TechAIProjectPython
description: Create or modify Python application components with clear separation of concerns, early returns, and deterministic pytest coverage. Use when building Python services, FastAPI or Flask apps, Python libraries, or when the user needs module scaffolding, service layers, or Python project structure guidance.
---

# Python Project Skill

## When to use
- Services, use cases, adapters, and modules in Python applications.
- Refactoring or extending existing Python application components.
- Non-script Python code that contains business behavior.

## Mandatory rules
- Keep business logic separated from I/O and infrastructure concerns.
- Keep module boundaries clear: business rules in one place, external integrations in another.
- Use clear, domain-relevant naming in classes, methods, and errors.
- Prefer early return and guard clauses.
- Keep code explicit and readability-first.
- Add unit tests for testable logic.
- Follow `.github/instructions/python.instructions.md` for dependency locking.

## Testing
- Use `pytest`.
- Keep tests deterministic and isolated.
- Prefer BDD-like names in the `given_when_then` style.
- For modify tasks with existing tests: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

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

## Minimal test example
```python
import pytest


def test_given_blank_account_id_when_creating_then_raises_value_error() -> None:
    with pytest.raises(ValueError):
        AccountId(" ")
```
