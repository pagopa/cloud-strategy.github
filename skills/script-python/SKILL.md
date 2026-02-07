---
name: script-python
description: Create Python scripts with logging, error handling, and optional tests.
---

# Python Script Skill

## When to use
- Automation scripts.
- Data processing (CSV, JSON, Parquet).
- API integrations.
- Reporting and analytics.

## Output language rule
- Docstrings, code comments, and log messages must be in English.

## Template

```python
#!/usr/bin/env python3
"""
{script_name}.py

Purpose: {description}
Usage: python {script_name}.py [options]
"""

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    logger.info("Starting {script_name}")

    try:
        # Implementation here
        _ = args
    except Exception as exc:
        logger.error(f"Error: {exc}")
        return 1

    logger.info("Completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Test template

Create `tests/test_{script_name}.py`:

```python
from {script_name} import main


def test_main_success() -> None:
    # Test implementation
    assert main() in (0, 1)
```

## Checklist
- [ ] Type hints are used on functions.
- [ ] Docstrings are in English.
- [ ] Error handling uses `try/except`.
- [ ] Logging is in English.
- [ ] CLI arguments use argparse.
