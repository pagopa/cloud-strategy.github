---
name: internal-python-project
description: Use when Python work primarily changes reusable imported behavior in importable packages, libraries, applications, services, or framework-owned flows; do not use when the primary contract is direct execution.
---

# Python Project Skill

## Boundary

This skill owns reusable imported behavior in Python packages, libraries,
applications, services, and framework-owned flows. It applies the complete
project baseline directly and does not require another skill.

## When to use

- Imported packages, libraries, applications, services, and framework-owned
  behavior whose primary contract is reusable code.
- Thin CLI or transport adapters whose stable contract remains imported
  project behavior.
- A CLI or toolkit with a `lib/` folder is judged by its primary contract: when
  the primary contract is reusable imported behavior, keep it here; when the
  primary contract is direct execution through multiple entrypoints, route to
  `/internal-python-script`.

## When not to use

- Do not use when the primary contract is direct execution through a standalone
  script, CLI, automation entrypoint, or operator-facing toolkit.
- Do not use for an unresolved mixed change until repository evidence
  establishes reusable imported behavior as the primary contract.

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
