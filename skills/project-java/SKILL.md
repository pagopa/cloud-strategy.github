---
name: project-java
description: Create or modify Java project components with purpose JavaDoc, readable flow, and JUnit tests.
---

# Java Project Skill

## When to use
- Java services, handlers, controllers, and utilities.
- Existing Java project components that require refactoring or extension.
- Java modules that need deterministic unit test coverage.

## Mandatory rules
- Add top JavaDoc with purpose.
- Use emoji logs for start/progress/error/completion.
- Prefer early return and guard clauses.
- Keep code readable and avoid over-engineering.
- Add JUnit 5 unit tests for testable logic.

## Template

```java
/**
 * Purpose: {description}
 */
public final class {component_name}Service {

    private final UserRepository userRepository;

    public {component_name}Service(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public UserResult loadById(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("❌ userId is required");
        }

        System.out.println("🚀 Loading user");
        // Implementation here
        return userRepository.findById(userId);
    }
}
```

## Test template

Create `src/test/java/.../{component_name}ServiceTest.java`:

```java
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

class {component_name}ServiceTest {

    @Test
    @DisplayName("given blank userId when loading then throws validation error")
    void givenBlankUserId_whenLoadById_thenThrowsValidationError() {
        var service = new {component_name}Service(new InMemoryUserRepository());
        assertThrows(IllegalArgumentException.class, () -> service.loadById(" "));
    }
}
```

## Checklist
- [ ] Purpose is documented.
- [ ] Emoji logs are used for key states.
- [ ] Guard clauses use early return.
- [ ] Code is readability-first.
- [ ] JUnit tests are included for testable behavior.
