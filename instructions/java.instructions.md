---
applyTo: "**/*.java"
---

# Java Instructions

## Mandatory rules
- Start script-like entrypoints with a top-level JavaDoc that explains purpose.
- Use emoji logs for start, progress, warnings, and failures.
- Prefer early return to avoid deep nesting.
- Prioritize readability and maintainability over clever abstractions.
- Unit tests are required for testable logic.

## Style
- Follow standard Java naming conventions.
- Keep methods small and cohesive.
- Avoid static mutable state unless strictly necessary.

## Recommended structure
```java
/**
 * Purpose: Explain what this Java entrypoint does.
 */
public final class App {

    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("❌ Missing arguments");
            return;
        }

        System.out.println("🚀 Starting");
        // implementation
        System.out.println("✅ Completed");
    }
}
```

## Testing
- Use JUnit 5 (`org.junit.jupiter`) as the default test stack.
- Use BDD-style naming via `@DisplayName` and `given_when_then` test method names.
- Prefer deterministic unit tests and avoid network calls in unit scope.
