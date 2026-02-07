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
- **Test framework**: ${input:test_framework:python=repo-default|java=junit5|node=node:test}

## Instructions

1. Inspect `${input:target_file}` and identify testable behavior.
2. Add or update tests covering:
   - happy path
   - input validation and guard clauses
   - relevant edge cases
3. Keep tests deterministic and isolated (no network calls in unit scope).
4. Use a simple default stack:
   - Java: JUnit 5
   - Node.js: `node:test` + `node:assert/strict`
5. Prefer readability and simple assertions over complex test abstractions.
6. Use BDD-like naming (`given_when_then` or clear `describe`/`it` grouping).
7. If language is Python and external dependencies are needed for the script, ensure `requirements.txt` uses pinned versions.
8. Do not create unit tests for Bash unless explicitly requested.

## Validation
- Run the project's unit test command for the selected language/framework.
- Report which test cases were added and why.
