---
description: Create a new Python script with proper structure
name: new-python-script
agent: agent
---

# Create Python Script

## Context
Create a new Python script following PagoPA conventions.

## Required Inputs
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:src/scripts}

## Instructions

1. Use the skill in `.github/skills/script-python/SKILL.md`
2. Search existing scripts in the repository for patterns
3. Create the script with:
   - Proper shebang and docstring
   - argparse for CLI arguments
   - Logging with emoji prefixes
   - Type hints
   - Error handling
4. If tests are needed, create `tests/test_{script_name}.py`

## Validation
- Check for syntax errors
- Verify imports are available
