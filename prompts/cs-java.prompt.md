---
description: Create or modify Java project components with tests
name: cs-java
agent: agent
argument-hint: action=<create|modify> component_type=<service|controller|handler|utility|module> component_name=<name> purpose=<purpose> [target_path=<path>]
---

# Java Project Task

## Context
Create or modify Java project components with clear structure and test coverage.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Component type**: ${input:component_type:service,controller,handler,utility,module}
- **Component name**: ${input:component_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:src/main/java}

## Instructions

1. Use the skill in `.github/skills/project-java/SKILL.md`.
2. Reuse repository conventions for package naming and folder structure.
3. Create or update the component with:
   - top JavaDoc containing purpose
   - emoji logs for state transitions
   - early return guard clauses
   - readable, straightforward flow
4. If `action=modify`, preserve existing behavior unless explicit changes are requested.
5. Add or update unit tests under `src/test/java` using JUnit 5 (BDD-like naming with `@DisplayName` and `given_when_then`).

## Validation
- Ensure code compiles.
- Run unit tests.
