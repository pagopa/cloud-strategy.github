---
applyTo: "**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx"
---

# Node.js Instructions

## Mandatory rules
- Treat Node.js work as project-oriented (modules, handlers, services, adapters), not script-oriented.
- Add a concise top comment that explains purpose for new or changed core modules when intent is not obvious.
- Use emoji logs for key runtime states when adding or updating logging.
- Prefer early return and guard clauses.
- Prioritize readability and simple control flow.
- Unit tests are required for testable logic.

## Style
- Keep modules focused and composable.
- Validate inputs early.
- Avoid hidden side effects.

## Recommended structure
```javascript
/**
 * Purpose: Explain what this module is responsible for.
 */

function buildUserProfile(input) {
  if (!input?.id) {
    throw new Error("❌ id is required");
  }

  // implementation
  return { id: input.id, name: input.name ?? "unknown" };
}
```

## Testing
- Use built-in `node:test` with `node:assert/strict` as the default test stack.
- Prefer BDD-like structure using `describe`/`it` where available.
- Keep unit tests isolated and deterministic.
