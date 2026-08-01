---
name: internal-java
description: Use when Java language or source correctness, readability, resource handling, error behavior, or generic Maven/Gradle build metadata is the primary concern, including compiler release, toolchains, plugins, dependencies, reproducibility, and focused build validation. Do not use when module or domain design, API and concurrency architecture, or framework-managed runtime behavior determines correctness.
---

# Internal Java

## Referenced files

- `references/review-anti-patterns.md`: Evidence-oriented Java review defects.
  Load when a review needs Java-specific defect depth.

## When to use

- Java source edits or reviews where language-level correctness, readability,
  control flow, resource handling, error behavior, or boundary validation is
  the main concern.
- Generic Maven or Gradle metadata, including compiler release, toolchains,
  dependency intent, plugins, and reproducibility.
- Focused Java build validation when the application or framework architecture
  is already clear.

## When not to use

- Module, package, domain, API, collaborator, or concurrency architecture is
  the main concern.
- Framework-managed wiring, configuration, lifecycle, transactions, test
  contexts, or runtime semantics determine correctness.
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
- Keep application and library architecture outside this skill when package,
  module, domain, API, collaborator, or concurrency structure drives the work.
- Keep framework-specific parent, plugin, BOM, starter, bean, configuration,
  adapter, transaction, scheduling, test-context, service-connection, and
  runtime semantics outside this skill.

## Validation

- Run the nearest Maven or Gradle command already used by the repository.
- For build-file-only edits, run the closest syntax, dependency, or test task
  that proves the change.
