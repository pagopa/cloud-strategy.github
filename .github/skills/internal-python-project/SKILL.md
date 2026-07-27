---
name: internal-python-project
description: Use when Python imported behavior covers importable packages, libraries, applications, services, and framework-owned flows, while routing direct scripts and CLIs to internal-python-script.
---

# Python Project Skill

## Boundary and routing

This skill owns Python imported behavior: packages, libraries, applications,
services, and framework-owned flows. Directly executed scripts, CLIs,
automation, and operator-facing toolkits belong to `internal-python-script`.
The shared `internal-python` baseline is not a required preload; use it only
when a cross-cutting concern or unresolved ownership question remains.

## When to use

- Imported packages, libraries, applications, services, and framework-owned
  behavior whose primary contract is reusable code.
- Thin CLI or transport adapters whose stable contract remains imported
  project behavior; direct-execution tooling belongs to the script owner.

## Project contract

- Follow the repository's existing framework, dependency manager, test naming,
  module layout, and validation commands before introducing optional patterns.
- For new test conventions, prefer behavior-oriented names that describe the
  observable contract; match existing test naming when it is already defined.
- Keep public APIs and data contracts typed and explicit. Pass configuration
  through typed settings, constructor arguments, function parameters, or the
  framework's composition boundary rather than reading deployment defaults from
  reusable code.
- Choose async only when the workload is I/O-bound and the surrounding stack
  supports it cleanly; keep async flows end-to-end.
- Separate domain, service, persistence, transport, or framework concerns when separation improves observable coupling, reuse, or testability. Do not impose
  a fixed folder tree or generic catch-all modules without that evidence.
- Keep imported-module logs neutral, structured, or framework-native. Return
  typed results, events, DTOs, or framework responses from core code.
- Keep human-facing rendering at a CLI adapter boundary and keep JSON, API
  responses, events, and exported files as plain data. Use `rich` only when a
  human-facing CLI contract owns that dependency.
- Preserve the repository's declared dependency manager. For pip-managed
  requirements, keep exact pins and hashes in the owning lock artifact; use the
  other manager's canonical frozen or locked validation when applicable.

## References

- Load `references/common-mistakes.md` for the full imported-code mistake table.
- Load `references/examples.md` for a minimal importable module and focused
  test example.
- Load `references/logging-and-reporting.md` when a project needs structured
  logs, typed results, adapter rendering, or data-versus-human output guidance.

## Testing and validation

- Follow the repository's pytest defaults and keep the public API, service
  boundary, adapter contract, or framework seam under focused coverage when it
  changes.
- Mock true external boundaries; do not mock internal business logic seams by
  default. Use parameterization or fixtures when they reduce duplication.
- Run the repository-declared syntax check, focused pytest command, and
  configured linter for changed behavior. For dependency changes, run the
  declared manager's canonical frozen or locked validation.
