---
description: Create a new Java CLI script/entrypoint with tests
name: new-java-script
agent: agent
argument-hint: class_name=<name> purpose=<purpose> [location=src/main/java]
---

# Create Java Script

## Context
Create a Java CLI entrypoint with clear structure and test coverage.

## Required inputs
- **Class name**: ${input:class_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:src/main/java}

## Instructions

1. Use the skill in `.github/skills/script-java/SKILL.md`.
2. Reuse repository conventions for package naming and folder structure.
3. Create the class with:
   - top JavaDoc containing purpose and usage examples
   - emoji logs for state transitions
   - early return guard clauses
   - readable, straightforward flow
4. Add unit tests under `src/test/java` using JUnit 5.

## Validation
- Ensure code compiles.
- Run unit tests.
