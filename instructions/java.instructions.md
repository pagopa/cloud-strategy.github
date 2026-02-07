---
applyTo: "**/*.java"
---

# Java Instructions

## Mandatory rules
- Treat Java work as project-oriented (services, modules, handlers, controllers, utilities), not script-oriented.
- Add a concise JavaDoc purpose comment to new or changed core classes when intent is not obvious.
- Use emoji logs for key runtime transitions when adding or updating logging.
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
 * Purpose: Explain what this component is responsible for.
 */
public final class UserService {

    public UserResult loadUser(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("❌ userId is required");
        }

        // implementation
        return new UserResult(userId);
    }
}
```

## Testing
- Use JUnit 5 (`org.junit.jupiter`) as the default test stack.
- Use BDD-like naming via `@DisplayName` and `given_when_then` test method names.
- Prefer deterministic unit tests and avoid network calls in unit scope.
