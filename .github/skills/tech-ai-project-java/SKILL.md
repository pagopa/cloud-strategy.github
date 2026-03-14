---
name: TechAIProjectJava
description: Create or modify Java project components with purpose JavaDoc and simple BDD-like unit tests. Use when building Java services, Spring Boot apps, Java libraries, or when the user needs class scaffolding, service layers, repository patterns, or Java-specific project structure guidance.
---

# Java Project Skill

## When to use
- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## Mandatory rules
- Keep business logic separated from I/O and infrastructure concerns (SDK calls, persistence, external APIs).
- Use clear, domain-relevant naming for classes, methods, and exceptions.
- Add concise purpose JavaDoc for new/changed core classes when intent is not obvious.
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
- For modify tasks with existing tests: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

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
