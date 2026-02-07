---
name: script-python
description: Create Python scripts with purpose docstring, emoji logs, early return patterns, unit tests, and pinned requirements when needed.
---

# Python Script Skill

## When to use
- Automation scripts.
- Data processing (CSV, JSON, Parquet).
- API integrations.
- Reporting and analytics.

## Mandatory rules
- Start with a docstring that includes purpose and usage examples.
- Use emoji logs for execution states.
- Prefer early return guard clauses.
- Keep implementation readable and explicit.
- Add unit tests for testable behavior.
- If external libraries are required, add/update `requirements.txt` with pinned versions.

## Template

```python
#!/usr/bin/env python3
"""
Purpose: {description}

Usage examples:
  python {script_name}.py --help
  python {script_name}.py --input data.json
"""

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--input", required=True, help="Input file path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input:
        logger.error("❌ Missing --input")
        return 1

    logger.info("🚀 Starting {script_name}")
    # Implementation here
    logger.info("✅ Completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Test template

Create `tests/test_{script_name}.py`:

```python
from {script_name} import main


def test_main_success() -> None:
    # Arrange / Act / Assert
    assert main() in (0, 1)
```

## Checklist
- [ ] Purpose and usage examples are in the module docstring.
- [ ] Type hints are used on functions.
- [ ] Emoji logging is used consistently.
- [ ] Early return guard clauses are used.
- [ ] Unit tests are included for testable behavior.
- [ ] `requirements.txt` is pinned when external dependencies are used.
