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
   - module docstring containing purpose and usage examples
   - argparse for CLI arguments
   - emoji logging
   - early return guard clauses
   - readable and explicit control flow
4. Create tests in `tests/test_{script_name}.py` for testable behavior.
5. If external libraries are required, create/update `requirements.txt` with pinned versions.

## Validation
- Check syntax errors.
- Verify import availability.
- Run unit tests.
