---
name: TechAIPairArchitectAnalysisExecutor
description: Templates, decision-table format, and validation rules for re-evaluating an ANALYSIS_REPORT and producing an EXECUTION_PLAN.
---

# Pair Architect Analysis Executor Skill

## When to use
- After `TechAIPairArchitect` has produced an `ANALYSIS_REPORT.md`.
- To critically verify each finding against the actual codebase.
- To generate a validated, sequenced `EXECUTION_PLAN.md` ready for `TechAIImplementer`.

## Decision table format

For **each** finding produce exactly this table (no empty cells):

```markdown
#### [<ORIGINAL-ID>] <Finding title>

| Aspect | Detail |
|---|---|
| **What the analysis says** | <Concise summary of finding and recommendation> |
| **Why it says it** | <Reasoning and evidence cited> |
| **Agreement** | ✅ Agree / ⚠️ Partially Agree / ❌ Disagree |
| **Motivation** | <Evidence-based justification — file paths, line numbers, git history> |
| **Concrete action** | <Exact changes or "No action" with justification> |
| **Effort** | Low / Medium / High |
| **Priority** | P0 (blocker) / P1 (before merge) / P2 (next sprint) / P3 (backlog) |
```

Group tables by original report section (Errors, Improvements, Doubts, Blind Spots, Architecture, Devil's Advocate).

## Report template — EXECUTION_PLAN.md

All five sections are mandatory.

### Section 1 — Executive Summary
3-5 sentences: what the analysis found, how many findings validated vs challenged, analysis quality assessment, proposed approach.

### Section 2 — Finding-by-Finding Evaluation
One decision table per finding (format above).

### Section 3 — Lessons Learned

| Subsection | Content |
|---|---|
| 3.1 Recurring Patterns | Table: Pattern / Affected Findings / Root Cause / Systemic Fix |
| 3.2 Repository Maturity Insights | Prose: strengths, weaknesses, direction |
| 3.3 Prevention Mechanisms | Table: Gap / Proposed Prevention / Type (Tooling/Process/Convention) |
| 3.4 Knowledge Gaps | Prose: areas needing better docs or understanding |

### Section 4 — Execution Plan

| Subsection | Content |
|---|---|
| 4.1 Work Packages | Table: # / Name / Findings Addressed / Actions / Effort / Priority / Dependencies |
| 4.2 Execution Sequence | Ordered list with rationale |
| 4.3 Risk Assessment | Table: Risk / Impact / Mitigation / Rollback |
| 4.4 Validation Criteria | Table: Work Package / Validation Method / Expected Result |

### Section 5 — Summary for Validation

Checklist for user approval:

```markdown
- [ ] **WP-1**: <one-line summary> (P0, effort: Low)
- ...

### Key Decisions Requiring Attention
1. **[<ID>]**: Disagreement — <reason>. Alternative: <action>.
```

## Disagreement protocol

When disagreeing with a finding:
1. Mark ❌ in the decision table.
2. Cite concrete evidence (file, line, git history).
3. Explain what the analysis missed.
4. Propose alternative or "No action".
5. Surface in Section 5 "Key Decisions".

## Quality checklist

- [ ] Every decision table is complete — no empty cells.
- [ ] Every "Concrete action" is specific enough for `TechAIImplementer` without re-analysis.
- [ ] Every disagreement includes evidence, not opinion.
- [ ] Execution plan is dependency-ordered.
- [ ] Effort estimates are realistic.
- [ ] Lessons Learned contains systemic insights, not finding repetitions.
- [ ] Work packages are grouped by logical affinity, not listed 1:1 per finding.

## Validation
- Every finding from `ANALYSIS_REPORT.md` must appear exactly once in `EXECUTION_PLAN.md`.
- Every disagreement must cite repository evidence.
- `EXECUTION_PLAN.md` must include all five mandatory sections and complete decision tables.
