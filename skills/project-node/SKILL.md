---
name: project-node
description: Create or modify Node.js project modules with purpose comments and simple BDD-like unit tests.
---

# Node.js Project Skill

## When to use
- Services, handlers, adapters, and utility modules.
- Refactoring or extending existing Node.js components.

## Mandatory rules
- Add a concise top purpose comment for new/changed core modules.
- Use emoji logs for key runtime states when logging is touched.
- Prefer early return and guard clauses.
- Keep code readable and straightforward.
- Add unit tests for testable logic.

## Test stack
- Built-in `node:test` + `node:assert/strict`.
- BDD-like grouping (`describe`/`it`) when available.
