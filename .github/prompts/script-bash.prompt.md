---
description: Create or modify reusable Bash scripts with strict mode and maintainable flow
name: script-bash
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [target_path=<path>]
---

# Create Bash Script

## Context
Use this prompt to create or modify Bash scripts for repository automation with generic, reusable behavior.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:.github/scripts}

## Instructions
1. Use `.github/skills/script-bash/SKILL.md` as implementation reference.
2. Start scripts with `#!/usr/bin/env bash` and strict mode.
3. Keep logs in English and include concise usage examples.
4. Prefer guard clauses and straightforward control flow.
5. Avoid consumer-repository assumptions in paths, credentials, and business semantics.

## Minimal example
- Input: `action=create script_name=check_frontmatter purpose="Validate required markdown metadata" target_path=.github/scripts`
- Expected output:
  - New Bash script with argument parsing, clear failures, and reusable checks.

## Validation
- Run `bash -n <script>`.
- Run `shellcheck -s bash <script>` when available.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
