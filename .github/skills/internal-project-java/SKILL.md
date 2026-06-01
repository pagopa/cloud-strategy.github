---
name: internal-project-java
description: Use when creating or modifying Java project code and the main concern is Java application structure, tests, or library/service design rather than Spring Boot framework choices.
---

# Java Project Skill

## When to use

- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## When not to use

- Spring Boot framework behavior drives the work; use `internal-spring-boot-development`.
- Build-system behavior is generic Make, YAML, or CI rather than Java-specific.

## Compact Java baseline

- Keep business logic separate from I/O, persistence, SDK calls, and transport adapters.
- Prefer clear domain names, guard clauses, and readable control flow.
- Add concise JavaDoc only when a new or changed core type has non-obvious intent.
- Use JUnit 5 for unit tests unless the repository has another established test stack.
- Keep dependency, plugin, runtime, and test intent explicit in Maven or Gradle files.

## Project-specific guidance

- Prefer constructor injection and immutable dependencies in Spring components.
- Keep controllers thin, services stateless, and API DTOs separate from persistence entities.
- Use Java 21 features only when the project already targets them or the runtime requirement is explicit.

Load `references/examples.md` when you need a minimal class or test example.

## Test stack

- Follow the JUnit 5 defaults.
- Use `@ParameterizedTest`, `assertAll`, `@Nested`, and `@Tag` when they improve test clarity rather than just adding ceremony.
- Use Spring test slices such as `@WebMvcTest` or `@DataJpaTest` before defaulting to full-context tests.
- Use Testcontainers when integration tests need real databases or external dependencies.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Spring coordination

- Keep Spring-specific design decisions lightweight here and treat controller, configuration, repository, or test-slice-heavy work as a separate framework-focused lane.
- Prefer constructor injection with `private final` dependencies and keep transaction boundaries narrow.

## Modern Java guidance

- Prefer records for small immutable data carriers when the codebase already uses them.
- Use sealed hierarchies only when bounded polymorphism is a real domain constraint.
- Consider virtual threads for high-concurrency I/O-heavy flows only when the framework and blocking model are understood.
- Reach for Testcontainers and profiling before speculative JVM tuning.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- Compile with `mvn compile` or `gradle build`.
- Run tests with `mvn test` or `gradle test`.
- Check code style with project linter when available.
