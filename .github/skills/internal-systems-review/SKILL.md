---
name: internal-systems-review
description: Use when a review needs systems-level evidence about architecture, workflow, cross-cutting impact, blind spots, or merge risk beyond line-level code defects.
---

# Internal Systems Review

Use this skill as the systems-level review lens for repository changes. It
complements defect-first code review by checking whether a change fits the
surrounding architecture, workflow, ownership model, and operational context.

## When to use

- Analyze a branch diff, PR, retained plan, or file list for systems-level risk.
- Evaluate architectural implications, workflow impact, and unconsidered effects.
- Review cross-cutting concerns before merge when line-level findings are not enough.
- Complement `internal-code-review` with broader evidence about coupling, ownership, and operational fit.

## When not to use

- Use `internal-code-review` for line-level defects, language anti-patterns, tests, and file-specific findings.
- Use `internal-gateway-critical-master` for pre-mortems, hidden-assumption tests, and pressure testing.
- Use a promoted `internal-security-review` only after that skill exists; until then, route security-specific gaps through the closest existing owner and state the gap.
- Do not turn advisory architecture notes into mandatory changes without evidence.

## Relationship to other skills

- `internal-code-review`: code defects, regressions, tests, language anti-patterns, and file/line findings.
- This skill: architecture, workflow, cross-cutting impact, operational fit, and blind spots.
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

## Output structure

Present findings directly in conversation (never write files unless the user explicitly asks):

1. **Findings** — systems-level risks ordered by severity, with evidence and fix route.
2. **Evidence gaps** — validation, context, or dependency information still missing.
3. **Blind spots** — realistic concerns the current change does not address.
4. **Architecture notes** — non-binding structural guidance with impact and effort.
5. **Summary** — brief overall assessment after findings.

For empty sections, state "No findings in this category."

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Flagging code style as a systems issue | Inflates findings and dilutes trust | Use `internal-code-review` for nit-level checks |
| Making ungrounded findings ("this might break X") | Speculation ≠ evidence | Every finding must cite a concrete file and line from the diff |
| Scope creep — analyzing the entire codebase | The user asked about a specific change | Analyze only changed files and their immediate dependencies |
| Reporting without effort estimation | Leaves the author without prioritization signal | Always include Low/Medium/High effort per finding |
| Treating advisory notes as blockers | Obscures urgency | Block only on evidenced systems risk |
| Skipping blind-spot analysis | The most valuable part of this skill gets dropped | Run all 4 dimensions, even if some are empty |

## Self-questioning

Before presenting findings, verify:

- Is this finding based on evidence in the diff, or am I assuming?
- Could I be wrong about the intent of this change?
- Am I flagging something that is actually fine for this specific context?
- What is the simplest correct interpretation?

## Workflow

1. Identify changed files (diff against default branch or explicit file list).
2. Load applicable instruction files based on detected languages.
3. Read each changed file and its immediate dependencies.
4. Analyze across all dimensions (load `references/analysis-dimensions.md` for detailed checklists).
5. Self-question each finding before including it.
6. Route code defects back to `internal-code-review` when they are not systems-level issues.
7. Present findings in conversation using the output structure above.

## Validation

- Every finding must reference a concrete file and line number.
- Every finding must include a *why* explanation.
- Every finding must include a minimal fix route or recommended owner.
- Architecture recommendations must include impact and effort assessment.
- Security-specific gaps must not imply `internal-security-review` exists before promotion.
