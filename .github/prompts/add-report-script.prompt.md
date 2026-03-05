---
agent: agent
description: Add a new cost report or analysis script
---

# Add Cost Report Script

## Context

This prompt helps you create a new cost analysis or reporting script.

## Input Required

- **Script Name**: ${input:scriptName}
- **Cloud Provider**: ${input:provider:azure,aws}
- **Description**: ${input:description}

## Instructions

1. Create the script in appropriate folder:
   - Azure: `azure/rel/`
   - AWS: `aws/`

2. Use this template:

```python
#!/usr/bin/env python3
"""
Script Name: ${input:scriptName}.py
Description: ${input:description}
Usage: python ${input:scriptName}.py [options]
Author: PagoPA Cloud Engineering
"""

import logging
import argparse
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    logger.info("🚀 Starting ${input:scriptName}...")

    try:
        # Implementation
        result = process()
        logger.info("✅ Completed successfully")
    except Exception as e:
        logger.error("❌ Failed: %s", e)
        raise


def process() -> Dict:
    """Process cost data."""
    # Implementation
    pass


if __name__ == "__main__":
    main()
```

3. Add dependencies to `requirements.txt`

## Validations

- [ ] Type hints included
- [ ] Docstrings complete
- [ ] Error handling implemented
- [ ] Logging with emoji prefixes
- [ ] Dependencies documented

## References

Follow the conventions in `#file:.github/instructions/python.instructions.md`
