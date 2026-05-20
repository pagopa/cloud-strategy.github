---
name: internal-high-level-review
description: Use when a task needs systems-level evidence about architecture, workflow, cross-cutting impact, blind spots, merge risk, or an orientation map of unfamiliar code.
---

# Internal High-Level Review

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `internal-code-review`: line-level defect review owner.
- `internal-gateway-critical-master`: pressure-test owner when the main need is challenge rather than review evidence.
- `internal-security-review`: unavailable future security lens, used only after promotion creates the skill.
- `superpowers-verification-before-completion`: evidence gate before claiming no systems findings or merge readiness.

Use this skill as the systems-level owner for repository changes and unfamiliar
code orientation. It complements defect-first code review by checking whether a
change fits the surrounding architecture, workflow, ownership model, and
operational context.

## When to use

- Analyze a branch diff, PR, retained plan, or file list for systems-level risk.
- Evaluate architectural implications, workflow impact, and unconsidered effects.
- Review cross-cutting concerns before merge when line-level findings are not enough.
- Complement `internal-code-review` with broader evidence about coupling, ownership, and operational fit.
- Build a higher-level orientation map for unfamiliar code, including relevant
  modules, callers, boundaries, and repository domain vocabulary.

## When not to use

- Use `internal-code-review` for line-level defects, language anti-patterns, tests, and file-specific findings.
- Use `internal-gateway-critical-master` for pre-mortems, hidden-assumption tests, and pressure testing.
- Use a promoted `internal-security-review` only after that skill exists; until then, route security-specific gaps through the closest existing owner and state the gap.
- Do not turn advisory architecture notes into mandatory changes without evidence.
- Do not introduce `CONTEXT.md`, ADR folders, or glossary maintenance as a side
  effect of review unless those structures already exist and the user asks to
  adopt them.

## Relationship to other skills

- `internal-code-review`: code defects, regressions, tests, language anti-patterns, and file/line findings.
- This skill: architecture, workflow, cross-cutting impact, operational fit,
  blind spots, and higher-level codebase orientation.
- `internal-gateway-critical-master`: challenge work when the main need is pressure testing rather than review evidence.
- Future `internal-security-review`: security, AI safety, trust boundaries, data, and secret exposure after promotion gates pass.

## Analysis dimensions

Dimensions are loaded from `references/analysis-dimensions.md` when deeper checklists are needed. Summary:

1. **Correctness** — Does the code do what the change claims? Edge cases? Error paths? Input validation?
2. **Separation of concerns** — Business vs I/O? Module boundaries? Naming clarity? Dependency direction? Interface stability?
3. **Architecture** — Coupling, cohesion, extensibility, testability, operational readiness?
4. **Blind spots** — Temporal analysis, team dynamics, cross-service impact, operational burden, data implications, security surface, performance cliffs, configuration drift, missing observability, alternative solutions?

## Workflow Review Lenses

Load the workflow references when review evidence needs more detail than the
main skill should carry:

- `references/plan-completion-audit.md`: plan-vs-diff mapping, completion
  status, and `UNVERIFIABLE` evidence gaps.
- `references/scope-drift.md`: declared intent, observed delivery, out-of-scope
  changes, and missing requirements.
- `references/review-lenses.md`: always-on, cross-cutting, and stack-specific
  review lenses with severity and confidence calibration.
- `references/audit-dispatch.md`: optional subagent dispatch for heavy plan or
  diff audits, with main-assistant spot checks.

Workflow findings should cover plan-vs-diff mapping, scope drift, evidence gaps,
contract coverage, and governance drift when those dimensions are in scope.

## Architecture Fit Lenses

Use these lenses when a review crosses module, workflow, or ownership boundaries:

- **Locality**: Does the change concentrate related knowledge, bugs, and future
  edits in one place, or does it force maintainers to chase behavior across
  several files?
- **Leverage**: Does the interface hide meaningful behavior behind a small
  contract, or does every caller still need to understand the implementation?
- **Module depth**: A deep module has a small interface and useful behavior
  behind it. A shallow module mostly passes complexity through to its callers.
- **Deletion test**: If the module vanished, would complexity disappear, or
  would the same complexity reappear across multiple callers?
- **Real seam test**: One adapter can be hypothetical. Two or more real users of
  a seam make the abstraction easier to justify.
- **Cross-boundary fit**: Check whether a change belongs in the touched owner,
  an adjacent internal skill, a reference, a validator, or a generated catalog
  artifact before recommending more files.

Keep these as review lenses, not mandatory refactor demands. Recommend a
deepening change only when the evidence shows current shallowness is creating
real maintenance, testability, or workflow cost.

## Orientation Map Lens

Use this lens when the user asks to zoom out, understand an unfamiliar area, or
see how code fits into the larger system before planning, reviewing, or editing.

Keep the output evidence-based and compact:

- Target area: the file, module, workflow, or behavior being explained.
- Domain vocabulary: repository terms that name the concepts in play.
- Module map: relevant modules, responsibilities, dependencies, and callers.
- Flow map: the main data, control, or operational path through those modules.
- Boundary notes: ownership, extension points, and cross-boundary risks.
- Uncertainty: missing evidence, likely next files to inspect, or validation gaps.

Do not turn orientation into review findings unless the user asks for a review
or the inspected evidence exposes a concrete systems risk.

## Severity mappings

| Category | Severity | Criteria |
| --- | --- | --- |
| Error | Critical | Security flaw, data loss risk, correctness bug affecting business logic |
| Error | Major | Missing error handling, broken contract, regression risk |
| Improvement | Readability | Code clarity, naming, structure |
| Improvement | Performance | Algorithmic efficiency, resource usage |
| Improvement | Maintainability | Technical debt, coupling, cohesion |
| Improvement | Testability | Test coverage gaps, untestable designs |
| Improvement | Security | Hardening, least privilege, input validation |

| Effort | Meaning |
| --- | --- |
| Low | Less than 1 hour, isolated change |
| Medium | 1-4 hours, may touch multiple files |
| High | More than 4 hours, may require design discussion |

## Review Output

Present findings directly in conversation (never write files unless the user explicitly asks):

1. **Findings** — systems-level risks ordered by severity, with evidence and fix route.
2. **Evidence gaps** — validation, context, or dependency information still missing.
3. **Blind spots** — realistic concerns the current change does not address.
4. **Architecture notes** — non-binding structural guidance with impact and effort.
5. **Summary** — brief overall assessment after findings.

For empty sections, state "No findings in this category."

## Orientation Output

When the request is explanatory rather than review-owned, present a map instead
of findings:

1. **Target Area** — the file, module, workflow, or behavior being explained.
2. **Domain Vocabulary** — repository terms that matter for the area.
3. **Module Map** — modules, responsibilities, dependencies, and callers.
4. **Flow Map** — main data, control, or operational path.
5. **Boundary Notes** — ownership, extension points, and risks to respect.
6. **Uncertainty** — missing evidence and next files or checks.

Do not include empty review sections in an orientation-only answer.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Flagging code style as a systems issue | Inflates findings and dilutes trust | Use `internal-code-review` for nit-level checks |
| Making ungrounded findings ("this might break X") | Speculation ≠ evidence | Every finding must cite a concrete file and line from the diff |
| Scope creep — analyzing the entire codebase | The user asked about a specific change | Analyze only changed files and their immediate dependencies |
| Reporting without effort estimation | Leaves the author without prioritization signal | Always include Low/Medium/High effort per finding |
| Treating advisory notes as blockers | Obscures urgency | Block only on evidenced systems risk |
| Skipping blind-spot analysis | The most valuable part of this skill gets dropped | Run all 4 dimensions, even if some are empty |
| Treating orientation as critique | The user may only need a codebase map | Separate maps from findings unless a concrete risk is evidenced |

## Self-questioning

Before presenting findings, verify:

- Is this finding based on evidence in the diff, or am I assuming?
- Could I be wrong about the intent of this change?
- Am I flagging something that is actually fine for this specific context?
- What is the simplest correct interpretation?

## Workflow

1. Identify changed files (diff against default branch or explicit file list).
2. Load applicable instruction files based on detected languages.
3. Read each changed file or requested target area and its immediate dependencies.
4. Analyze across all dimensions, or build an orientation map when the request
   is explanatory rather than review-owned. Load
   `references/analysis-dimensions.md` for detailed checklists.
5. For review-owned work, self-question each finding before including it.
6. Route code defects back to `internal-code-review` when they are not systems-level issues.
7. Present review findings or an orientation map using the matching output
   structure above.

## Validation

- Every finding must reference a concrete file and line number.
- Every finding must include a *why* explanation.
- Every finding must include a minimal fix route or recommended owner.
- Architecture recommendations must include impact and effort assessment.
- Orientation maps must name the target area, domain vocabulary, module map,
  caller or entrypoint evidence, boundary notes, and uncertainty.
- Security-specific gaps must not imply `internal-security-review` exists before promotion.
- Use `superpowers-verification-before-completion` before claiming there are no
  systems findings, the review is complete, or the change is merge-ready.
