---
description: Create a new Python script with a standard structure
name: new-python-script
agent: agent
argument-hint: script_name=<name> purpose=<purpose> [location=src/scripts]
---

# Create Python Script

## Context
Create a new Python script following PagoPA standards.

## Required inputs
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:src/scripts}

## Instructions

1. Use the skill in `.github/skills/script-python/SKILL.md`.
2. Search for existing scripts in the repository to reuse patterns.
3. Create the script with:
   - shebang and docstring
   - argparse for CLI arguments
   - structured logging
   - type hints
   - explicit error handling
4. If needed, create tests in `tests/test_{script_name}.py`.
5. Generate code and operational messages in English (docstrings, logs, error messages).

## Validation
- Check syntax errors.
- Verify import availability.
