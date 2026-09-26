---
name: internal-python-project
description: Use when Python work changes reusable imported code, such as packages, libraries, SDKs, services, framework handlers, thin CLI adapters over package code, or their tests. Route standalone scripts and automation entrypoints to /internal-python-script, and mixed or unclear ownership to /internal-python.
---

# Python Project Skill

## When to use

This skill owns Python work whose primary contract is reusable imported
behavior:

- packages, libraries, applications, services, and framework-owned flows;
- thin CLI or transport adapters whose stable contract remains the imported
  project behavior;
- a CLI or toolkit with a `lib/` folder when its primary contract is reusable
  imported behavior.

It applies the complete project baseline itself. Route direct execution
through standalone scripts, standalone CLIs, automation entrypoints, or
multi-entrypoint operator toolkits to `/internal-python-script`. Route a mixed
change whose primary contract is still unresolved to `/internal-python`.

## Workflow

1. **Confirm the contract.** Identify the public API, service boundary,
   adapter, or framework seam that the change touches. **Complete when:** the
   imported contract and its consumers are named.
2. **Apply the project contract.** Follow the rules below and the repository's
   existing conventions. **Complete when:** each changed module satisfies
   every contract rule, applying repository conventions only where a rule
   defers to them.
3. **Validate.** Run the checks in
   [Testing and validation](#testing-and-validation). **Complete when:** each
   check has an observed result or a named evidence gap.

## Project contract

- Follow the repository's existing framework, test naming, module layout, and
  validation commands before introducing optional patterns.
- For new test conventions, prefer behavior-oriented names that describe the
  observable contract; match existing test naming when it is already defined.
- Keep public APIs and data contracts typed and explicit. Pass configuration
  through typed settings, constructor arguments, function parameters, or the
  framework's composition boundary rather than reading deployment defaults from
  reusable code.
- Choose async only when the workload is I/O-bound and the surrounding stack
  supports it cleanly; keep async flows end-to-end.
- Separate domain, service, persistence, transport, or framework concerns when
  separation improves observable coupling, reuse, or testability. Do not impose
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
