---
name: TechAIPairArchitect
description: Deep change-impact analysis with DDD focus, structured Markdown report generation, and lateral thinking for blind spots.
---

# Pair Architect Skill

## When to use
- Analyze a set of repository changes (branch diff, PR, or file list) for correctness, design, and blind spots.
- Generate a structured `ANALYSIS_REPORT.md` with actionable findings.
- Evaluate domain modeling, bounded context integrity, and architectural alignment.
- Complement line-level code review with systems-level and business-level thinking.

## Relationship to other skills
- **TechAICodeReview**: focuses on per-line anti-patterns and severity catalogs. Use it for exhaustive nit-level scanning.
- **TechAIPairArchitect** (this skill): focuses on change-set-level impact, DDD alignment, architectural implications, and unconsidered aspects. Use it for holistic analysis.
- Both skills can be used together: run `TechAICodeReview` for detailed findings, then `TechAIPairArchitect` for the bigger picture.

## Analysis dimensions

### 1. Correctness analysis
- Does the code do what the change claims?
- Are edge cases handled?
- Are error paths tested?
- Is input validation present and sufficient?

### 2. Domain-Driven Design analysis
Evaluate against these DDD principles:

| Principle | What to check |
|---|---|
| Bounded contexts | Are context boundaries clear? Does the change leak domain concepts across boundaries? |
| Ubiquitous language | Do class/method/variable names use domain terminology consistently? |
| Aggregates | Are aggregate roots properly guarding invariants? Is there transactional boundary leakage? |
| Entities vs Value Objects | Are identities correctly modeled? Are immutable concepts modeled as value objects? |
| Domain services | Is business logic placed in the domain layer or scattered in application/infrastructure? |
| Anti-corruption layers | When integrating with external systems, is there a translation layer? |
| Repository pattern | Is persistence abstracted from domain logic? |

#### DDD smell catalog

Use these IDs when flagging DDD violations:

##### Critical
| ID | Smell | Why |
|---|---|---|
| DDD-C01 | Domain logic in infrastructure layer | Business rules coupled to I/O, untestable without external dependencies |
| DDD-C02 | Aggregate invariant bypassed via direct child access | Data consistency guarantee broken, corruption risk |
| DDD-C03 | Shared mutable state across bounded contexts | Tight coupling destroys independent deployability |

##### Major
| ID | Smell | Why |
|---|---|---|
| DDD-M01 | Anemic domain model | Business logic in application or service layer instead of entities or value objects |
| DDD-M02 | God aggregate (> 5 entities or > 3 collections) | Transaction scope too wide, performance and contention risk |
| DDD-M03 | Ubiquitous language drift | Technical naming instead of domain terminology — cognitive gap grows over time |
| DDD-M04 | Cross-context direct import | Module A imports domain types from Module B without anti-corruption layer |
| DDD-M05 | Repository returns infrastructure types | Domain layer depends on persistence details |
| DDD-M06 | Domain events carrying infrastructure concerns | Events should be pure domain facts, not transport metadata |
| DDD-M07 | Use case orchestration in domain entities | Entities should guard invariants, not coordinate workflows |

##### Minor
| ID | Smell | Why |
|---|---|---|
| DDD-m01 | Value object modeled as entity (has identity but no lifecycle) | Over-engineering, unnecessary complexity |
| DDD-m02 | Missing factory method for complex aggregate creation | Construction logic scattered, hard to enforce invariants |
| DDD-m03 | Domain service doing what an entity method could do | Misplaced responsibility, weaker encapsulation |
| DDD-m04 | Specification pattern missing for complex business rules | Rules scattered across multiple locations |
| DDD-m05 | Missing domain event for a significant state transition | Reduced observability and extensibility |

##### Nit
| ID | Smell | Why |
|---|---|---|
| DDD-N01 | Inconsistent naming between code and domain glossary | Language drift signal |
| DDD-N02 | Bounded context boundary not documented | Implicit knowledge, onboarding friction |
| DDD-N03 | Aggregate methods not named with domain verbs | Verbs like `process()` or `handle()` obscure intent |

### 3. Architecture analysis
Evaluate structural qualities:

| Quality | What to check |
|---|---|
| Separation of concerns | Are domain, application, infrastructure, and presentation layers distinct? |
| Dependency direction | Do dependencies point inward (infrastructure -> application -> domain)? |
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
| DDD | Domain modeling, bounded context, ubiquitous language |
| Security | Hardening, least privilege, input validation |

### Effort estimation
| Level | Meaning |
|---|---|
| Low | Less than 1 hour, isolated change |
| Medium | 1-4 hours, may touch multiple files |
| High | More than 4 hours, may require design discussion |

## Health score

Compute a numeric health score (0-100) for the change set and include it in the Executive Summary.

### Calculation
- Start at 100.
- For each finding, subtract points based on severity:

| Finding type | Points deducted per instance |
|---|---|
| Critical error | -20 |
| Major error | -10 |
| Blind spot | -5 |
| Improvement opportunity | -2 |
| Doubt or open question | -1 |

- Floor at 0 (never go negative).
- Architecture recommendations (advisory) do not affect the score.

### Verdict thresholds
| Score | Verdict | Meaning |
|---|---|---|
| 90-100 | Excellent | Ready to merge with confidence |
| 70-89 | Good | Minor issues, safe to merge after addressing them |
| 50-69 | Needs Work | Significant issues that should be resolved before merge |
| 30-49 | Poor | Major rework needed, consider design discussion |
| 0-29 | Critical | Do not merge — blocking issues present |

## Risk matrix

For the top findings (up to 8), place them on a 2x2 risk matrix in the report:

```
                    HIGH IMPACT
                        │
         URGENT         │       PLAN
     (fix before merge) │  (fix in next sprint)
                        │
  ──────────────────────┼──────────────────────
                        │
        MONITOR         │       ACCEPT
     (watch in prod)    │    (low risk, defer)
                        │
                    LOW IMPACT
       HIGH PROBABILITY          LOW PROBABILITY
```

For each placed finding, state: `[<ID>] <title> → <quadrant>`.

## Report template

Generate the report following this structure (all sections mandatory):

1. **Executive Summary** — 2-4 sentences on what changed and overall assessment.
2. **Errors and Defects** — Objectively wrong things with fix suggestions.
3. **Improvement Opportunities** — Working code that can be better, with effort estimates.
4. **Doubts and Open Questions** — Ambiguous areas requiring author clarification.
5. **Blind Spots and Unconsidered Aspects** — Things the change does not address but should.
6. **Architecture and Best Practices (Advisory)** — Non-binding DDD and architecture guidance.
7. **Devil's Advocate** (only when `mode=devil`) — Adversarial challenges to design assumptions.
8. **Risk Matrix** — Top findings placed on probability/impact grid.
9. **Summary Statistics** — Counts per category and health score.

For empty sections, state "No findings in this category" explicitly.

## Devil's advocate mode

When invoked with `mode=devil`, apply an adversarial analysis layer:

1. Find at least 3 fundamental objections to the chosen design approach.
2. For each objection, propose a radically different alternative with tradeoffs.
3. Challenge assumptions that seem obvious — ask "what if this premise is wrong?"
4. Consider the worst-case scenario for each major design decision.
5. Write a dedicated section `## 6. Devil's Advocate` between Architecture and Risk Matrix.

Format:
```markdown
### [DEVIL-<NNN>] <provocative question>
- **Assumption challenged**: <what the change takes for granted>
- **What if it is wrong**: <consequence>
- **Alternative approach**: <radically different solution>
- **Tradeoffs**: <pros and cons vs current approach>
```

## Git history awareness

When analyzing a change set, also gather recent repository context:

1. Read recent commit history (`git log --oneline -20`) to understand project direction.
2. Check for patterns: are similar changes being made repeatedly? Is there churn?
3. Use this context in the Blind Spots section to flag:
   - Misalignment with recent project trajectory.
   - Repeated patterns that suggest a systemic issue needing a different solution.
   - Abandoned or reverted approaches being reintroduced.

## Workflow

1. Identify changed files (diff against default branch or explicit file list).
2. Load applicable instruction files based on detected languages.
3. Read each changed file and its immediate dependencies.
4. Analyze across all dimensions (correctness, DDD, architecture, blind spots).
5. Write findings into the report template.
6. Compute health score and populate risk matrix.
7. If `mode=devil`, run adversarial analysis and add Devil's Advocate section.
8. Save as `ANALYSIS_REPORT.md` at repository root.
9. Report completion with summary statistics and health score.

## Validation
- Every finding must reference a concrete file and line number.
- Every finding must include a *why* explanation.
- Every error or improvement must include a *how to fix* suggestion.
- Architecture recommendations must include impact/effort assessment.
- Health score must be computed and verdict must match the threshold table.
- Risk matrix must contain the most impactful findings (up to 8).
- If `mode=devil`, at least 3 Devil's Advocate challenges must be present.
- The report must be valid Markdown with no broken links or formatting.

