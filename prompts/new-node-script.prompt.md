---
description: Create a new Node.js script with tests
name: new-node-script
agent: agent
argument-hint: script_name=<name> purpose=<purpose> [location=scripts]
---

# Create Node.js Script

## Context
Create a Node.js script with clear behavior and unit tests.

## Required inputs
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:scripts}

## Instructions

1. Use the skill in `.github/skills/script-node/SKILL.md`.
2. Reuse existing repository conventions for module format and folder layout.
3. Create the script with:
   - top comment block containing purpose and usage examples
   - emoji logs for runtime progress
   - early return guard clauses
   - readability-first implementation
4. Add unit tests using the repository test framework (`node:test`, Jest, or Vitest).

## Validation
- Run lint/type checks if present.
- Run unit tests.
