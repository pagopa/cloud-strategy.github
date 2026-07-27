---
name: internal-java-spring-boot-development
description: Use when Spring Boot runtime or framework semantics drive work involving dependency management, bean wiring, configuration, HTTP or data adapters, scheduling, transactions, test contexts, service connections, or Boot virtual-thread enablement. Do not use for ordinary Java edits, generic Maven/Gradle metadata, or framework-neutral application design.
---

# Internal Spring Boot Development

## Referenced skills

- `internal-java`: Ordinary Java source and generic Maven/Gradle metadata.
- `internal-java-project`: Framework-neutral Java application, library, service,
  package, domain, API, and collaborator structure.

Route adjacent work to those owners when Spring Boot semantics do not
determine correctness. Keep this skill focused on the active Boot branch.

## When to use

- Spring Boot behavior determines correctness: dependency management, bean
  wiring, configuration binding, HTTP or data adapters, scheduling,
  transactions, test contexts, service connections, or virtual-thread
  enablement.
- The task depends on Boot parent, plugin, BOM, starter, auto-configuration,
  lifecycle, annotation, context, or executor semantics.

## Workflow

1. Identify the active Boot line, Java compatibility, build parent or plugin,
   wrapper, and framework surface. Check the current project and official
   documentation before relying on version-sensitive behavior.
2. Decide whether the active branch is HTTP/configuration, persistence/data,
   testing, dependency management, bean wiring, scheduling, transactions, or
   runtime execution. Load only the matching reference.
3. Keep framework-managed adapters at the edge and domain behavior in plain
   collaborators that remain easy to test. Use explicit required dependencies,
   typed configuration, focused stereotypes, and narrow transaction boundaries.
4. Choose the smallest Spring context that proves the framework behavior. Use
   the checked-in wrapper and repository task for validation.

## References

- Load `references/http-config.md` when the task is mainly about controllers, request/response DTOs, validation, exception mapping, or application configuration.
- Load `references/testing-and-data.md` when the task is mainly about repositories, transactions, test slices, containerized integration tests, or data-access boundaries.
- Load `references/runtime-semantics.md` when the task is mainly about Boot dependency management, bean wiring, transactions, scheduling, startup behavior, or virtual-thread enablement.

## Branch guidance

- Keep controllers thin: validate input, map transport types, delegate once,
  and preserve the established response contract.
- Keep services focused on business behavior and use plain collaborators when
  the framework adds no value.
- Bind and validate structured configuration at startup, and keep configuration
  holders focused on environment binding rather than service behavior.
- Preserve framework misconfiguration as an observable startup or test failure;
  do not mask it with defensive fallbacks.
- Follow the existing properties/YAML format and project conventions unless a
  migration is part of the task.

## Validation

- Identify the project's existing Java build and test command before running it.
- Prefer `./mvnw`, `mvn`, `./gradlew`, or the checked-in equivalent over generic
  guesses, and validate the smallest affected context before widening scope.
