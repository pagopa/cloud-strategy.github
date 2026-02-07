---
description: Create a new Bash script with a standard structure
name: new-bash-script
agent: agent
argument-hint: script_name=<name> purpose=<purpose> [location=scripts]
---

# Create Bash Script

## Context
Create a new Bash script following PagoPA standards.

## Required inputs
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:scripts}

## Instructions

1. Use the skill in `.github/skills/script-bash/SKILL.md`.
2. Search for existing scripts in the repository to reuse patterns.
3. Create the script with:
   - `#!/usr/bin/env bash`
   - initial comment block with purpose and usage examples
   - `set -euo pipefail`
   - emoji logging functions
   - early return guard clauses
   - readable and simple control flow
4. Do not add unit tests for Bash unless explicitly requested.
5. Make the file executable.

## Validation
- Run `bash -n` on the script.
- Run `shellcheck -s bash` when available.
