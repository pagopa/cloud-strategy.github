---
name: script-python
description: Create Python scripts with logging, error handling, and optional tests. Use for data processing, automation, and API interactions.
---

# Python Script Skill

## When to Use
- Creating automation scripts
- Data processing (CSV, JSON, Parquet)
- API interactions
- Cost analysis and reporting

## Template

```python
#!/usr/bin/env python3
"""
📋 {script_name}.py

🎯 Purpose: {description}
📖 Usage: python {script_name}.py [options]
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    logger.info("🔍 Starting {script_name}")
    
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    logger.info("✅ Completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Test Template

Create `tests/test_{script_name}.py`:

```python
import pytest
from {script_name} import main

def test_main_success():
    # Test implementation
    pass
```

## Checklist
- [ ] Type hints on all functions
- [ ] Docstrings for public functions
- [ ] Error handling with try/except
- [ ] Logging with emoji prefixes
- [ ] argparse for CLI arguments
