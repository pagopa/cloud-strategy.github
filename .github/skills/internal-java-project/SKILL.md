---
name: internal-java-project
description: Use when creating or modifying Java project code and the main concern is Java application structure, tests, or library/service design rather than Spring Boot framework choices.
---

# Java Project Skill

## Referenced skills

Treat the referenced skill below as an on-demand owner. Do not preload it for
every Java project edit; load it only when Spring Boot framework behavior is
the main constraint.

- `internal-java-spring-boot-development`: Spring Boot controllers, configuration, repositories, scheduling, and Spring test-slice depth.

## When to use

- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## When not to use

- Spring Boot framework behavior drives the work; use `internal-java-spring-boot-development`.
- Build-system behavior is generic Make, YAML, or CI rather than Java-specific.

## Compact Java baseline

- Keep business logic separate from I/O, persistence, SDK calls, and transport adapters.
- Prefer clear domain names, guard clauses, and readable control flow.
- Add concise JavaDoc only when a new or changed core type has non-obvious intent.
- Use JUnit 5 for unit tests unless the repository has another established test stack.
- Keep dependency, plugin, runtime, and test intent explicit in Maven or Gradle files.

## Boundary

- Keep machine-readable output stable and undecorated at data boundaries, and keep human-friendly formatting at CLI or UI boundaries only.
- Keep logs structured with contextual keys and avoid mixing log streams with program output consumed by tools.
- Validate external input at transport and persistence boundaries before state changes.
- Use `Optional` at boundaries where absence is expected and avoid `null` as hidden control flow.

## Project-specific guidance

- Prefer constructor injection and immutable dependencies in Spring components.
- Keep controllers thin, services stateless, and API DTOs separate from persistence entities.
- Split-or-justify any class or service that trends toward a god class role with mixed responsibilities.
- Use Java 21 features only when the project already targets them or the runtime requirement is explicit.
- Prefer immutable domain types and final fields by default.
- Prefer static factory methods when constructor intent is ambiguous.
- Prefer composition over inheritance unless bounded polymorphism is a true domain constraint.

Load `references/examples.md` when you need a minimal class or test example.

## Test stack

- Follow the JUnit 5 defaults.
- Use `@ParameterizedTest`, `assertAll`, `@Nested`, and `@Tag` when they improve test clarity rather than just adding ceremony.
- Use Spring test slices such as `@WebMvcTest` or `@DataJpaTest` before defaulting to full-context tests.
- Use Testcontainers when integration tests need real databases or external dependencies.
- For behavior changes or bug fixes, keep focused tests on observable service, controller, module, or boundary behavior and rerun the narrowest meaningful test set before widening scope.
- For pure refactors, keep behavior stable and run compile plus existing tests before and after.
- Mock only external boundaries and keep internal collaborators real where practical.
- Prefer targeted coverage for changed behavior and boundary failures over broad percentage goals.

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
