---
description: Create or modify a Java CLI script/entrypoint with tests
name: cs-java-script
agent: agent
argument-hint: action=<create|modify> class_name=<name> purpose=<purpose> [location=src/main/java] [target_file=<path>]
---

# Java Script Task

## Context
Create or modify a Java CLI entrypoint with clear structure and test coverage.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Class name**: ${input:class_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:src/main/java}
- **Target file (when modifying)**: ${input:target_file}

## Instructions

1. Use the skill in `.github/skills/script-java/SKILL.md`.
2. Reuse repository conventions for package naming and folder structure.
3. Create or update the class with:
   - top JavaDoc containing purpose
   - emoji logs for state transitions
   - early return guard clauses
   - readable, straightforward flow
4. If `action=modify`, preserve existing behavior unless explicit changes are requested.
5. Add or update unit tests under `src/test/java` using JUnit 5 (BDD-like naming with `@DisplayName` and `given_when_then`).

## Validation
- Ensure code compiles.
- Run unit tests.
