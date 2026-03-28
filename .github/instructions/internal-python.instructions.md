---
description: Python standards for both scripts and application code with DDD boundaries, guard clauses, and pytest defaults.
applyTo: "**/*.py"
---

# Python Instructions

## Mandatory rules
- Use emoji logs for key execution states.
- Prefer early return and clear guard clauses.
- Keep code explicit and readable.
- Prefer the standard library first. Introduce well-maintained third-party libraries when they materially simplify code and reduce custom logic.
- Do not reinvent common parsing/validation/serialization behavior when the standard library or a well-maintained library provides a clearer solution.
- Prefer simple, readable, and easily modifiable code over clever abstractions.
- Accept additional lines or mild redundancy when it improves clarity, maintainability, and safe future changes.
- Unit tests are required for testable logic.
- Apply these rules for both create and modify operations.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.
- Keep template content complete and externalize only values intentionally passed by the caller.

## Application code (non-script)
- For non-trivial features, keep business logic separated from I/O and infrastructure concerns.
- Keep module boundaries clear: business rules in one place, external integrations in another.
- Use clear, domain-relevant naming in classes, methods, and errors.

## Script code
- Start scripts with a module docstring containing purpose and usage examples.
- Keep CLI parsing and orchestration explicit.
- Avoid embedding domain rules that belong to reusable application modules.

## Style
- Follow PEP8.
- Use type hints in function signatures.
- Keep line length <= 120.

## Output language
- Docstrings, logs, exceptions, and CLI output must be in English.

## Dependencies
- Standardize on `requirements.txt` as the Python dependency lock artifact in this baseline.
- If external libraries are introduced, prefer a compiled `requirements.txt` with exact `==` pins, full transitive dependency closure, and `--hash` entries for every locked requirement.
- Keep a short comment above each introduced dependency block so the pinned version is readable without parsing the full hash line.
- Recommend third-party libraries when they materially reduce custom parsing, validation, HTTP, CLI, serialization, or retry code.
- Do not force third-party libraries over the standard library when the standard library is simpler, clearer, or safer.
- When a fully hash-locked `requirements.txt` is not feasible, use exact `==` pins in `requirements.txt` and document the reason in the closest technical note or workflow comment.

## Dependency example
```text
# requests 2.32.3
requests==2.32.3 \
    --hash=sha256:<hash1> \
    --hash=sha256:<hash2>
```

- Generate the locked file with `pip-compile --generate-hashes` or an equivalent workflow that captures the full dependency closure.

## Testing defaults
- Use `pytest` as default unit-test framework.
- Keep tests under `tests/` with deterministic behavior.
- For modify tasks with existing tests: edit code first, run existing tests, then update tests only if behavior changes are intentional.

## Minimal skeleton
```python
#!/usr/bin/env python3
"""Purpose: Explain what this script does.

Usage examples:
  python script.py --help
"""
```

## Minimal test example
```python
def test_example() -> None:
    assert 1 + 1 == 2
```
