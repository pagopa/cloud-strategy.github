---
name: script-python
description: Create or modify Python scripts with purpose docstring, emoji logs, tests, and pinned dependencies when needed.
---

# Python Script Skill

## When to use
- New Python scripts.
- Existing Python scripts that need updates.

## Mandatory rules
- Module docstring must include purpose and usage examples.
- Use emoji logs for execution states.
- Prefer early return and guard clauses.
- Keep implementation explicit and readable.
- Add unit tests for testable behavior.
- If external libraries are needed, pin `requirements.txt`.

## Minimal template
```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  python {script_name}.py --help
"""
```

## Testing
- Put tests under `tests/`.
- Keep tests deterministic and isolated.
