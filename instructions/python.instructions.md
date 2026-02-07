---
applyTo: "**/*.py"
---

# Python Instructions

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
"""Script description."""

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("Starting...")
    # implementation
    logger.info("Completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Dependencies
- Pin dependency versions using the toolchain adopted by the repository.
- Use virtual environments when applicable.
