---
description: Create or modify a Node.js script with tests
name: cs-node-script
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [location=scripts] [target_file=<path>]
---

# Node.js Script Task

## Context
Create or modify a Node.js script with clear behavior and unit tests.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:scripts}
- **Target file (when modifying)**: ${input:target_file}

## Instructions

1. Use the skill in `.github/skills/script-node/SKILL.md`.
2. Reuse existing repository conventions for module format and folder layout.
3. Create or update the script with:
   - top comment block containing purpose
   - emoji logs for runtime progress
   - early return guard clauses
   - readability-first implementation
4. If `action=modify`, preserve existing behavior unless explicit changes are requested.
5. Add or update unit tests using `node:test` + `node:assert/strict` (BDD-like `describe`/`it` style where available).

## Validation
- Run lint/type checks if present.
- Run unit tests.
