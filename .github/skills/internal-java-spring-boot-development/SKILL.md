---
name: internal-java-spring-boot-development
description: Use when Spring Boot-specific framework or runtime semantics determine correctness, including parent, plugin, BOM, starter, auto-configuration, bean wiring, configuration binding, HTTP or data adapters, scheduling, transactions, test contexts, service connections, or virtual-thread enablement. Do not use for ordinary Java source work, generic Maven/Gradle metadata, or framework-neutral application and library design.
---

# Internal Spring Boot Development

## When to use

- Spring Boot behavior determines correctness: dependency management, bean
  wiring, configuration binding, HTTP or data adapters, scheduling,
  transactions, test contexts, service connections, or virtual-thread
  enablement.
- The task depends on Boot parent, plugin, BOM, starter, auto-configuration,
  lifecycle, annotation, context, or executor semantics.

## When not to use

- Route ordinary Java source correctness or generic Maven/Gradle metadata to
  /internal-java when no Spring Boot-specific behavior determines the outcome.
- Route framework-neutral module, package, domain, API, collaborator,
  concurrency, or test design to /internal-java-project.

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
