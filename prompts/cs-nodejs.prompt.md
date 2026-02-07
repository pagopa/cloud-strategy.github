---
description: Create or modify Node.js project modules with tests
name: cs-nodejs
agent: agent
argument-hint: action=<create|modify> component_type=<service|handler|module|utility|adapter> component_name=<name> purpose=<purpose> [target_path=<path>]
---

# Node.js Project Task

## Context
Create or modify Node.js project modules with clear behavior and unit tests.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Component type**: ${input:component_type:service,handler,module,utility,adapter}
- **Component name**: ${input:component_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:src}

## Instructions

1. Use the skill in `.github/skills/project-nodejs/SKILL.md`.
2. Reuse existing repository conventions for module format and folder layout.
3. Create or update the component with:
   - top comment block containing purpose
   - emoji logs for runtime progress
   - early return guard clauses
   - readability-first implementation
4. If `action=modify`, preserve existing behavior unless explicit changes are requested.
5. Add or update unit tests using `node:test` + `node:assert/strict` (BDD-like `describe`/`it` style where available).

## Validation
- Run lint/type checks if present.
- Run unit tests.
