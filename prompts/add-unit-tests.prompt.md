---
description: Add or improve unit tests for Python, Java, or Node.js code
name: add-unit-tests
agent: agent
argument-hint: language=<python|java|node> target_file=<path> [test_framework=<name>]
---

# Add Unit Tests

## Context
Add or improve unit tests for an existing script or module while preserving repository conventions.

## Required inputs
- **Language**: ${input:language:python,java,node}
- **Target file**: ${input:target_file}
- **Test framework**: ${input:test_framework:repo-default}

## Instructions

1. Inspect `${input:target_file}` and identify testable behavior.
2. Add or update tests covering:
   - happy path
   - input validation and guard clauses
   - relevant edge cases
3. Keep tests deterministic and isolated (no network calls in unit scope).
4. Prefer readability and simple assertions over complex test abstractions.
5. If language is Python and external dependencies are needed for the script, ensure `requirements.txt` uses pinned versions.
6. Do not create unit tests for Bash unless explicitly requested.

## Validation
- Run the project's unit test command for the selected language/framework.
- Report which test cases were added and why.
