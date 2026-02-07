---
applyTo: "**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx"
---

# Node.js Instructions

## Mandatory rules
- Start script files with a top comment that explains purpose and usage examples.
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
 * Usage examples:
 *   node script.js --help
 *   node script.js --input data.json
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
- Use the test framework already adopted by the repository (`node:test`, Jest, or Vitest).
- Keep unit tests isolated and deterministic.
