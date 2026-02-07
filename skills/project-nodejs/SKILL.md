---
name: project-nodejs
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

## Minimal module example
```javascript
/** Purpose: Build a user profile response. */
function buildUserProfile(input) {
  if (!input?.id) {
    throw new Error("❌ id is required");
  }
  return { id: input.id, name: input.name ?? "unknown" };
}
```

## Test stack
- Built-in `node:test` + `node:assert/strict`.
- BDD-like grouping (`describe`/`it`) when available.

## Minimal test example
```javascript
const test = require("node:test");
const assert = require("node:assert/strict");

test("given missing id when building profile then throws", () => {
  assert.throws(() => buildUserProfile({}), /id is required/);
});
```
