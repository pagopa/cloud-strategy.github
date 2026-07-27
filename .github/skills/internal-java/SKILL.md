---
name: internal-java
description: Use when editing or reviewing Java source or generic Maven/Gradle metadata and the main concern is language-level correctness, readability, dependency intent, compiler release, toolchains, or focused build validation. Do not use when application architecture or Spring Boot runtime semantics drive the work.
---

# Internal Java

## Referenced skills

Treat the referenced skills below as on-demand owners. Load them only when the
task proves which owner is needed.

- `internal-java-project`: Framework-neutral Java application and library
  structure, domain boundaries, APIs, concurrency, or contract tests.
- `internal-java-spring-boot-development`: Spring Boot dependency management,
  wiring, configuration, adapters, scheduling, transactions, test contexts,
  service connections, or Boot virtual-thread semantics.

## Referenced files

- `references/review-anti-patterns.md`: Evidence-oriented Java review defects.
  Load when `internal-review-code` or another review caller needs Java-specific
  defect depth.

## When to use

- Java source edits or reviews where language-level correctness, readability,
  control flow, resource handling, error behavior, or boundary validation is
  the main concern.
- Generic Maven or Gradle metadata, including compiler release, toolchains,
  dependency intent, plugins, and reproducibility.
- Focused Java build validation when the application or framework architecture
  is already clear.

## When not to use

- Application or library structure is the main concern; use
  `internal-java-project`.
- Spring Boot runtime semantics drive the work; use
  `internal-java-spring-boot-development`.
- Build-system behavior is generic Make, YAML, or CI rather than Java-specific.

## Working contract

- Keep ordinary Java logic readable: use clear names, explicit control flow,
  narrow responsibilities, safe resource handling, and meaningful error
  behavior.
- Validate external or public-boundary input before invalid state reaches core
  logic. Preserve established contracts for nullability, exceptions, and
  output.
- Discover the repository's compiler release, Java toolchain, runtime target,
  Maven or Gradle wrapper, dependency-management mechanism, and established
  test stack before recommending version-sensitive changes.
- Keep compiler, toolchain, dependency-intent, plugin, and reproducibility
  guidance aligned with the repository's existing build. Prefer the checked-in
  wrapper and the repository's established validation tasks.
- Route application or library design to `internal-java-project` when package,
  module, domain, API, collaborator, or concurrency structure drives the work.
- Route Boot parent, plugin, BOM, starter, bean, configuration, adapter,
  transaction, scheduling, test-context, service-connection, or virtual-thread
  semantics to `internal-java-spring-boot-development`.

## Validation

- Run the nearest Maven or Gradle command already used by the repository.
- For build-file-only edits, run the closest syntax, dependency, or test task
  that proves the change.
