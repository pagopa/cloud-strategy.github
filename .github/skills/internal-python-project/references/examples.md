# Python Project Examples

## Minimal importable contract

`account_status.py`

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

## Focused test

Follow the repository's configured import ordering and test naming. This
example keeps the subject importable and tests its public contract.

```python
import pytest

from account_status import AccountId


def test_given_blank_account_id_when_creating_then_raises_value_error() -> None:
    with pytest.raises(ValueError):
        AccountId(" ")
```
