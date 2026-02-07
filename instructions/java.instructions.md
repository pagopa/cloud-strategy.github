---
applyTo: "**/*.java"
---

# Java Instructions

## Mandatory rules
- Treat work as project-oriented (services/modules/components), not script-oriented.
- Add concise purpose JavaDoc for new/changed core classes when intent is not obvious.
- Use emoji logs for key runtime transitions when logging is touched.
- Prefer early return and guard clauses.
- Prioritize readability and maintainability.
- Add unit tests for testable logic.

## Testing defaults
- Use JUnit 5.
- Use BDD-like naming: `@DisplayName` and `given_when_then`.
- Keep unit tests deterministic and isolated.

## Reference implementation
- For code and test examples, use `.github/skills/project-java/SKILL.md`.
