---
applyTo: "**/*.py"
---

# Python Instructions

## Mandatory rules
- Start each script with a module docstring that explains purpose and usage examples.
- Use emoji logs for key execution states.
- Prefer early return and clear guard clauses.
- Prioritize readability over compact or clever patterns.
- Unit tests are required for testable logic.

## Style
- Follow PEP8.
- Use type hints in function signatures.
- Maximum line length: 120 characters.

## Output language rules
- Generated docstrings must be in English.
- Logs, user-facing exceptions, and CLI output must be in English.

## Recommended structure
```python
#!/usr/bin/env python3
"""
Purpose: Explain what this script does.

Usage examples:
  python script.py --help
  python script.py --input data.json
"""

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Short purpose")
    parser.add_argument("--input", required=True, help="Input path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input:
        logger.error("❌ Missing required input")
        return 1

    logger.info("🚀 Starting script")
    # implementation
    logger.info("✅ Completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Dependencies
- If external libraries are required, add `requirements.txt` with pinned versions.
- Use virtual environments when applicable.
