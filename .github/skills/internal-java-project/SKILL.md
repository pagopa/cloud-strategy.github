---
name: internal-java-project
description: Use when designing or changing framework-neutral Java application or library structure, domain boundaries, APIs, concurrency, or unit and contract tests. Do not use when Spring Boot wiring, configuration, transactions, dependency management, or test contexts determine correctness.
---

# Java Project Skill

## Referenced skills

Treat the referenced skill below as an on-demand owner. Do not preload it for
every Java project edit; load it only when Spring Boot framework behavior is
the main constraint.

- `internal-java-spring-boot-development`: Spring Boot wiring, configuration,
  transactions, dependency management, HTTP or data adapters, scheduling,
  test contexts, service connections, and Boot runtime semantics.

## When to use

- Designing or changing framework-neutral Java modules, packages, services,
  libraries, domains, APIs, handlers, utilities, or collaborators.
- Refactoring application structure where boundaries, ownership, or domain
  behavior are the main concern.
- Choosing unit, contract, or narrow integration tests for behavior that does
  not depend on a framework lifecycle.

## When not to use

- Spring Boot wiring, configuration binding, transactions, HTTP or data
  adapters, scheduling, test contexts, service connections, or Boot runtime
  behavior determines correctness; use
  `internal-java-spring-boot-development`.
- Generic Java source or build metadata is the main concern; use
  `internal-java`.
- Build-system behavior is generic Make, YAML, or CI rather than Java-specific.

## Project design

- Give modules, packages, services, libraries, domains, APIs, and collaborators
  explicit boundaries and one clear reason to change.
- Keep domain behavior separate from I/O, persistence, SDK calls, and transport
  adapters. Use composition and bounded polymorphism when they express the
  domain better than inheritance.
- Make required dependencies explicit and keep state immutable where practical.
  Treat a growing collaborator set or mixed responsibility as a review cue for
  a narrower boundary.
- Use Java features compatible with the declared project support and existing
  codebase. Do not introduce a newer language feature without checking the
  compiler release and runtime target.

## Concurrency and tests

- For generic concurrency or virtual-thread suitability, check declared Java
  support, blocking-I/O workload, bounded downstream resources, context
  propagation, observability, and representative load behavior. Do not infer
  suitability from throughput claims alone.
- Select tests from repository evidence: use plain unit tests for isolated
  behavior, contract tests for stable boundaries, and narrow integration tests
  when a real external dependency is required to prove the contract.
- Use real external dependencies when mocks cannot prove serialization,
  persistence, protocol, or other boundary behavior. Keep setup representative
  and validation focused on observable outcomes.
- Validate inputs and preserve established output and error contracts at public
  boundaries. Keep machine-readable output stable and human formatting at the
  CLI or UI edge.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- Run the repository's wrapper or established compile and test commands.
- Check the project linter or formatter when available.
- Re-run the narrowest meaningful test set before widening validation.
