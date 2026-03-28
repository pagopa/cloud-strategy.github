---
name: internal-project-java
description: Create or modify Java project components with purpose JavaDoc and BDD-like unit tests. Use when building Java services, Spring Boot apps, Java libraries, class scaffolding, service layers, or repository patterns.
---

# Java Project Skill

## When to use
- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## Mandatory rules
- Keep business logic separated from I/O and infrastructure concerns.
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
- JUnit 5 with `@DisplayName` and `given_when_then` naming.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

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

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Business logic inside controller/handler | Untestable, tightly coupled to framework | Extract to a service class, inject via constructor |
| Catching `Exception` everywhere | Swallows unexpected errors, hides bugs | Catch specific exceptions; let runtime errors propagate |
| Mutable shared state in service classes | Thread-safety bugs in concurrent environments | Use immutable objects or proper synchronization |
| No null checks on external input | NullPointerException at runtime | Validate at entry point with guard clauses |
| Test names like `test1`, `testMethod` | No documentation value, hard to diagnose failures | Use `given_when_then` naming with `@DisplayName` |
| Over-using inheritance for code reuse | Rigid hierarchies, fragile base class problem | Prefer composition and delegation |

## Cross-references
- **TechAICodeReview** (`.github/skills/tech-ai-code-review/SKILL.md`): for reviewing Java code (see `references/anti-patterns-java.md`).
- **TechAIDocker** (`.github/skills/tech-ai-docker/SKILL.md`): for containerizing Java apps.

## Validation
- Compile with `mvn compile` or `gradle build`.
- Run tests with `mvn test` or `gradle test`.
- Check code style with project linter when available.
