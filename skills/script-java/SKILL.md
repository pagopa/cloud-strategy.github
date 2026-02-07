---
name: script-java
description: Create Java CLI entrypoints with purpose JavaDoc, emoji logs, early return flow, and JUnit tests.
---

# Java Script Skill

## When to use
- Java command-line entrypoints.
- Small utilities and maintenance jobs.
- Data transformation scripts in Java.

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
public final class {class_name} {

    private {class_name}() {
    }

    public static int run(String[] args) {
        if (args == null || args.length == 0) {
            System.err.println("❌ Missing arguments");
            return 1;
        }

        System.out.println("🚀 Starting {class_name}");
        // Implementation here
        System.out.println("✅ Completed");
        return 0;
    }

    public static void main(String[] args) {
        int exitCode = run(args);
        if (exitCode != 0) {
            System.exit(exitCode);
        }
    }
}
```

## Test template

Create `src/test/java/.../{class_name}Test.java`:

```java
import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

class {class_name}Test {

    @Test
    void runReturnsErrorWhenArgsAreMissing() {
        assertEquals(1, {class_name}.run(new String[]{}));
    }
}
```

## Checklist
- [ ] Purpose is documented.
- [ ] Emoji logs are used for key states.
- [ ] Guard clauses use early return.
- [ ] Code is readability-first.
- [ ] JUnit tests are included for testable behavior.
