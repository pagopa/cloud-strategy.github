---
name: project-java
description: Create or modify Java project components with purpose JavaDoc and simple BDD-like unit tests.
---

# Java Project Skill

## When to use
- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## Mandatory rules
- Add concise purpose JavaDoc for new/changed core classes.
- Use emoji logs for key runtime transitions when logging is touched.
- Prefer early return and guard clauses.
- Keep code readable and avoid over-engineering.
- Add unit tests for testable logic.

## Test stack
- JUnit 5.
- BDD-like naming with `@DisplayName` and `given_when_then`.
