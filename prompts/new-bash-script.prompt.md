---
description: Create a new Bash script with proper structure
name: new-bash-script
agent: agent
---

# Create Bash Script

## Context
Create a new Bash script following PagoPA conventions.

## Required Inputs
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:scripts}

## Instructions

1. Use the skill in `.github/skills/script-bash/SKILL.md`
2. Search existing scripts in the repository for patterns
3. Create the script with:
   - `set -euo pipefail`
   - Logging functions (log_info, log_success, log_error)
   - Usage/help function
   - Proper variable quoting
4. Make the script executable

## Validation
- Run `shellcheck` if available
- Test with `bash -n` for syntax
