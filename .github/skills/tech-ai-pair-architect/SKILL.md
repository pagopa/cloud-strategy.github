---
name: TechAIChangeImpactAnalysis
description: Change-impact analysis with correctness focus, architectural evaluation, and lateral thinking for blind spots. Use when the user wants to understand the ripple effects of a change, identify architectural risks in a changeset, review cross-cutting concerns before merge, or needs a holistic pre-merge impact assessment beyond line-level review.
---

# Change Impact Analysis Skill

## When to use
- Analyze a set of repository changes (branch diff, PR, or file list) for correctness, design, and blind spots.
- Evaluate architectural implications and unconsidered aspects of a change.
- Complement line-level code review with systems-level and business-level thinking.

## Relationship to other skills
- **TechAICodeReview**: focuses on per-line anti-patterns and severity catalogs. Use it for exhaustive nit-level scanning.
- **This skill**: focuses on change-set-level impact, architectural implications, and unconsidered aspects. Use it for holistic analysis.
- Both skills can be used together: run `TechAICodeReview` for detailed findings, then this skill for the bigger picture.

## Analysis dimensions

### 1. Correctness analysis
- Does the code do what the change claims?
- Are edge cases handled?
- Are error paths tested?
- Is input validation present and sufficient?

### 2. Separation of concerns analysis
| Principle | What to check |
|---|---|
| Business vs I/O | Is business logic cleanly separated from I/O, SDKs, and persistence? |
| Module boundaries | Are module boundaries clear and cohesive? |
| Naming clarity | Do names reflect what the code does in business terms? |
| Dependency direction | Do high-level modules avoid depending on low-level details? |
| Interface stability | Are module contracts (inputs/outputs) stable and documented? |

### 3. Architecture analysis
Evaluate structural qualities:

| Quality | What to check |
|---|---|
| Separation of concerns | Are business logic, I/O, and presentation layers distinct? |
| Dependency direction | Do dependencies point inward (infrastructure → application → core logic)? |
| Coupling | Is coupling between modules explicit and minimal? |
| Cohesion | Are related concepts grouped together? |
| Extensibility | Can this design accommodate likely future changes without significant rework? |
| Testability | Can each component be tested in isolation? |
| Operational readiness | Are logs, metrics, and health checks present for production visibility? |

### 4. Blind-spot detection
Apply lateral thinking:

- **Temporal analysis**: Will this change cause problems at scale? After 6 months of accumulation?
- **Team dynamics**: Does this change increase onboarding friction for new team members?
- **Cross-service impact**: Could this change break consumers or upstream producers?
- **Operational burden**: What happens when this fails at 3 AM? Can on-call engineers debug it?
- **Data implications**: Are there schema changes, migration needs, or data consistency risks?
- **Security surface**: Does this change expand the attack surface?
- **Performance cliffs**: Is there a hidden O(n²) or unbounded resource consumption?
- **Configuration drift**: Are there environment-specific assumptions that break in other stages?
- **Missing observability**: Can we know if something goes wrong after deployment?
- **Alternative solutions**: Is there a fundamentally simpler approach that was not considered?

## Severity mappings

### Errors and Defects
| Severity | Criteria |
|---|---|
| Critical | Security flaw, data loss risk, correctness bug affecting business logic |
| Major | Missing error handling, broken contract, regression risk |

### Improvements
| Category | Description |
|---|---|
| Readability | Code clarity, naming, structure |
| Performance | Algorithmic efficiency, resource usage |
| Maintainability | Technical debt, coupling, cohesion |
| Testability | Test coverage gaps, untestable designs |
| Security | Hardening, least privilege, input validation |

### Effort estimation
| Level | Meaning |
|---|---|
| Low | Less than 1 hour, isolated change |
| Medium | 1-4 hours, may touch multiple files |
| High | More than 4 hours, may require design discussion |

## Output structure

Present findings directly in conversation (never write files unless the user explicitly asks). Use this structure:

1. **Summary** — 2-4 sentences on what changed and overall assessment.
2. **Errors and defects** — Objectively wrong things with fix suggestions.
3. **Improvement opportunities** — Working code that can be better, with effort estimates.
4. **Open questions** — Ambiguous areas requiring author clarification.
5. **Blind spots** — Things the change does not address but should.
6. **Architecture notes** — Non-binding structural guidance (advisory only).

For empty sections, state "No findings in this category."

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
4. Analyze across all dimensions (correctness, separation of concerns, architecture, blind spots).
5. Self-question each finding before including it.
6. Present findings in conversation using the output structure above.

## Validation
- Every finding must reference a concrete file and line number.
- Every finding must include a *why* explanation.
- Every error or improvement must include a *how to fix* suggestion.
- Architecture recommendations must include impact/effort assessment.

