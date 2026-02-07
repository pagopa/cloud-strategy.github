---
name: project-java
description: Create or modify Java project components with purpose JavaDoc and simple BDD-like unit tests.
---

# Java Project Skill

## When to use
- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## Mandatory rules
- Add concise purpose JavaDoc for new/changed core classes.
- Use emoji logs for key runtime transitions when logging is touched.
- Prefer early return and guard clauses.
- Keep code readable and avoid over-engineering.
- Add unit tests for testable logic.

## Minimal class example
```java
/** Purpose: Resolve user by id with input validation. */
public final class UserService {
    public String resolveUserId(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("❌ userId is required");
        }
        return userId.trim();
    }
}
```

## Test stack
- JUnit 5.
- BDD-like naming with `@DisplayName` and `given_when_then`.

## Minimal test example
```java
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class UserServiceTest {
    @Test
    @DisplayName("given blank userId when resolving then throws")
    void givenBlankUserId_whenResolving_thenThrows() {
        var service = new UserService();
        assertThrows(IllegalArgumentException.class, () -> service.resolveUserId(" "));
    }
}
```
