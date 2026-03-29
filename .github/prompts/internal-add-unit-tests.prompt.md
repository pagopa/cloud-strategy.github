---
description: Add or improve unit tests for Python, Java, or Node.js code
name: internal-add-unit-tests
agent: agent
argument-hint: target_file=<path> [target_stack=<auto|python|java|nodejs>] [test_framework=<name>]
---

# Add Unit Tests

## Context
Add or improve unit tests for an existing Python, Java, or Node.js module while preserving repository conventions.

## Required inputs
- **Target file**: ${input:target_file}
- **Target stack**: ${input:target_stack:auto,python,java,nodejs}
- **Test framework**: ${input:test_framework:pytest}

## Instructions

1. Detect the target stack from `${input:target_file}` when possible; otherwise use `${input:target_stack}`.
2. Use the closest repository skill:
   - Python: `.github/skills/internal-project-python/SKILL.md` or `.github/skills/internal-script-python/SKILL.md`
   - Java: `.github/skills/internal-project-java/SKILL.md`
   - Node.js: `.github/skills/internal-project-nodejs/SKILL.md`
3. Inspect `${input:target_file}` and identify testable behavior.
4. Add or update tests covering:
   - happy path
   - input validation and guard clauses
   - relevant edge cases
5. Keep tests deterministic and isolated (no network calls in unit scope).
6. Prefer readability and simple assertions over complex test abstractions.
7. Use clear naming for test cases.
8. If external dependencies are needed for tests, ensure pinned versions where repository conventions require it.

## Minimal example
- Input: `target_file=src/scripts/report.py`
- Expected output:
  - Tests under `tests/` covering success, validation, and edge behavior.
  - Deterministic assertions and no network calls.

## Validation
- Run the closest stack-appropriate test command (`pytest`, a Maven/Gradle test task, or `npm`/`pnpm`/`yarn test`).
- Report which test cases were added and why.
