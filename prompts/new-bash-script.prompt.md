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
   - `set -euo pipefail`
   - logging functions
   - usage/help function
   - proper variable quoting
4. Make the file executable.
5. Generate code and operational messages in English (comments, `echo`, usage text).

## Validation
- Run `bash -n` on the script.
- Run `shellcheck -s bash` when available.
