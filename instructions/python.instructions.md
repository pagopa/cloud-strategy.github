---
applyTo: "**/*.py"
---

# Python Instructions

## Style
- Follow PEP8
- Use type hints for function signatures
- Maximum line length: 120 characters

## Structure
```python
#!/usr/bin/env python3
"""
Script description.
"""

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("🔍 Starting...")
    # implementation
    logger.info("✅ Completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Logging Prefixes
- 🔍 Info/Progress
- ✅ Success
- ❌ Error
- ⚠️ Warning

## Dependencies
- Pin versions in `requirements.txt`
- Use virtual environments
