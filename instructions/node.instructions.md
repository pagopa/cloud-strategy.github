---
applyTo: "**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx"
---

# Node.js Instructions

## Mandatory rules
- Start script files with a top comment that explains purpose.
- Use emoji logs for key runtime states.
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
 * Purpose: Explain what this script does.
 */

function main(argv) {
  if (!argv.includes("--input")) {
    console.error("❌ Missing --input");
    return 1;
  }

  console.log("🚀 Starting script");
  // implementation
  console.log("✅ Completed");
  return 0;
}

process.exit(main(process.argv.slice(2)));
```

## Testing
- Use built-in `node:test` with `node:assert/strict` as the default test stack.
- Prefer BDD-like structure using `describe`/`it` where available.
- Keep unit tests isolated and deterministic.
