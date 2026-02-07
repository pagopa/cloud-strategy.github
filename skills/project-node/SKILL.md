---
name: project-node
description: Create or modify Node.js project modules with purpose comments, readable flow, and unit tests.
---

# Node.js Project Skill

## When to use
- Node.js services, handlers, adapters, and utilities.
- Existing project modules that require refactoring or extension.
- JavaScript/TypeScript modules that need deterministic unit test coverage.

## Mandatory rules
- Add a top comment block with purpose.
- Use emoji logs for key execution states.
- Prefer early return and guard clauses.
- Keep code readable and straightforward.
- Add unit tests for testable behavior.

## Template

```javascript
/**
 * Purpose: {description}
 */

function buildUserProfile(input) {
  if (!input?.id) {
    throw new Error("❌ id is required");
  }

  console.log("🚀 Building user profile");
  // Implementation here
  return {
    id: input.id,
    name: input.name ?? "unknown",
  };
}

module.exports = { buildUserProfile };
```

## Test template

Create `tests/{component_name}.test.js`:

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");
const { buildUserProfile } = require("../{component_name}");

test("given missing id when building profile then throws", () => {
  assert.throws(() => buildUserProfile({}), /id is required/);
});
```

## Checklist
- [ ] Purpose is documented at the top.
- [ ] Emoji logs are used for key states.
- [ ] Guard clauses use early return.
- [ ] Code is readability-first.
- [ ] Unit tests are included for testable behavior.
