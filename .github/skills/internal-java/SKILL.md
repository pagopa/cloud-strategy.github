---
name: internal-java
description: Use when creating, editing, or reviewing Java files or Java build metadata before project or Spring depth is needed.
---

# Internal Java

## Referenced skills

Treat the referenced skills below as on-demand owners. Do not preload them for
every Java edit; load them only when the task proves which owner is needed.

- `internal-java-project`: Java package, module, service, library, and deterministic test design when application or library structure becomes the main concern.
- `internal-java-spring-boot-development`: Spring Boot controllers, configuration, repositories, scheduled jobs, and framework tests when framework behavior becomes the main concern.

## When to use

- `.java`, `pom.xml`, `build.gradle`, or `build.gradle.kts` changes.
- Lightweight Java reviews focused on readability, naming, dependency intent, tests, and boundary hygiene.
- Small Java edits where the project structure is already clear.

## When not to use

- Java application or library structure is the main concern; use `internal-java-project`.
- Spring Boot framework behavior drives the work; use `internal-java-spring-boot-development`.
- Build-system behavior is generic Make, YAML, or CI rather than Java-specific.

## Baseline

- Keep business logic separate from I/O, persistence, SDK calls, and transport adapters.
- Prefer clear domain names, guard clauses, and readable control flow.
- Add concise JavaDoc only when a new or changed core type has non-obvious intent.
- Use JUnit 5 for unit tests unless the repository has another established test stack.
- Keep dependency, plugin, runtime, and test intent explicit in Maven or Gradle files.

## Validation

- Run the nearest Maven or Gradle test command already used by the repository.
- For build-file-only edits, run the closest syntax, dependency, or test task that proves the change.
