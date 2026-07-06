---
name: internal-gateway-review
description: Use when repository-owned work needs defect-first review of a concrete non-code or mixed artifact, workflow, bundle, or review package before fixes.
---

# Internal Gateway Review

## Referenced skills

- `internal-gateway-critical-master`: final autonomous counter-check when findings, no-finding verdicts, or next-action choices need pressure before action.
- `internal-code-review`: route hint when code-only evidence needs dedicated line-level review.
- `internal-high-level-review`: route hint only when system-surface evidence needs broader architecture, workflow, or merge-risk review.
- `internal-ai-resource-review`: route hint only when AI-resource evidence needs deeper bundle, lifecycle, or catalog review.

Portable review gateway. Owns review scope, evidence discipline, findings
consolidation, decision-usefulness, and final counter-check for non-code or
mixed targets. It does not apply fixes, author retained plans, or preload
specialist review skills.

Use the target itself to choose review depth. Keep review thinking local unless
the user directly selected a specialist owner or a separate prompt already
selected one.

The specialist entries above are route hints, not preload instructions. Name the
surface and likely next owner when deeper review is needed, but do not load a
specialist just because its surface appears.

Before any user-visible verdict, counter-check the analysis for evidence,
severity, false positives, contrary evidence, scope narrowing, and decision
usefulness. Use `internal-gateway-critical-master` at the end when the review
depends on a material judgment, a no-finding claim, or a proposed next action.
Revise or reopen when the counter-check exposes a material gap.

## Workflow

```mermaid
flowchart TD
  A[Review request] --> B[Resolve concrete target]
  B --> C[Read smallest useful evidence]
  C --> D{Clarifying question changes the review?}
  D -->|Yes| E[Ask focused question block]
  E --> C
  D -->|No| F[Classify review surfaces]
  F --> G{Primary surface}
  G -->|Code| H[Review code surface locally]
  G -->|System| I[Review system surface locally]
  G -->|AI resource| J[Review AI-resource surface locally]
  G -->|Mixed| K[Review primary surface first, then secondary gaps]
   H --> L[Prefer internal-code-review when target is code-only]
  I --> L
  J --> L
  K --> L
  L --> M[Counter-validate findings]
  M --> N{Finding survives or no-finding claim is supported?}
  N -->|No| O[Reopen evidence, scope, or questions]
  O --> C
  N -->|Yes| P[Run critical counter-check]
  P --> Q{Critical check passes?}
  Q -->|No| O
  Q -->|Yes| R[Emit review gate and next decision]
  R --> S[Stop before fixes]
```

## Review Surface Selection

Select review surfaces from the changed paths, stated goal, and evidence gaps;
do not start from a single default lens. A diff may activate more than one
surface. This gateway names surfaces, not specialist skill dependencies.

When the target is purely code, prefer `internal-code-review` and stop before
stretching this gateway into a code-only reviewer. Use this gateway for code
only when the code is secondary evidence inside a broader artifact, workflow,
AI-resource, policy, plan, or mixed review.

- Code surface: changed source, scripts, tests, build files, dependency files,
  generated-code boundaries, and validation paths.
- System surface: architecture, workflow, ownership, rollout, cross-boundary
  impact, operational fit, and merge risk.
- AI-resource surface: repository-owned prompts, agents, skills, instructions,
  bundle siblings, catalog files, sync behavior, and customization drift.

When the diff is mainly AI customization assets, review the AI-resource surface
first and treat embedded scripts as a secondary code surface. Do not let a
language-oriented scan silently skip `.md` skill, agent, prompt, instruction, or
inventory files.

## Surface Routing Hints

Use these labels to classify evidence and name a likely next owner when deeper
review is needed. Route hints are not preload instructions.

| Surface | Evidence signals | Local review focus | Route hint |
| --- | --- | --- | --- |
| Code surface | Source, scripts, tests, build files, dependencies, generated-code boundaries | Decide whether the target is code-only; inspect embedded code only when it affects a mixed review | `internal-code-review` for dedicated line-level review |
| System surface | Architecture, workflow, ownership, rollout, cross-boundary impact, merge risk | Operational fit, coupling, scope drift, blind spots, and decision risk | `internal-high-level-review` for broader systems review |
| AI-resource surface | Skills, agents, prompts, instructions, inventory, sync behavior, bundle siblings | Retrieval, bundle self-containment, lifecycle, propagation, and customization drift | `internal-ai-resource-review` for deeper bundle or catalog review |

For mixed reviews, pick the dominant surface first, inspect only secondary
surfaces that affect material findings or residual risk, and consolidate the
verdict in this gateway.

## Review Procedure

1. Resolve the concrete target: artifact, diff, PR, workflow, bundle, retained
   report, or explicit file list.
2. Identify intent, anti-scope, changed surfaces, validation already run, and
   evidence gaps from the smallest useful local evidence.
3. Ask a focused question before analysis only when the answer would change
   scope, severity, owner, or the review decision.
4. Classify the primary and secondary review surfaces, then inspect the diff or
   target before reading immediate owning context.
5. Read more context only when a finding, route hint, or residual-risk claim
   needs it.
6. Check design fit, functionality, security, complexity, tests, naming,
   comments, documentation, consistency, and changed-user impact when relevant.
7. For each potential finding, test the contrary explanation before reporting
   it: intended behavior, local convention, compatibility, generated output,
   explicit user scope, or validator coverage.
8. Prefer `internal-code-review` when the target is code-only; otherwise name a route hint only when deeper specialist review would change confidence,
   severity, owner, validation, or the next decision.
9. Report at most 5 material findings unless exhaustive review is requested.
10. For low-finding or no-finding reviews, include evidence coverage, residual
   risk, and the next decision the reader can make.
11. Run the final `internal-gateway-critical-master` counter-check before the
   verdict and reopen the analysis if it changes severity, confidence, scope,
   or next action.

## Token Discipline

Inspect diff and failing evidence first; avoid broad repository scans unless an
evidence gap requires one. Prefer aggregate facts for large diffs, generated
files, tabular exports, and logs before reading raw volume. Summarize omitted
low-risk observations separately, not as findings.

Use `Compact Evidence Reporting` for large diffs, generated files, tabular
exports, and logs: keep findings defect-first, cite the smallest excerpt or
file point that proves impact, and avoid dumping large raw blocks when a
targeted excerpt plus evidence path preserves the same proof.

## Output Contract

Findings must lead, ordered by severity. Each material finding carries:

- finding and impact;
- severity and confidence;
- smallest evidence point;
- evidence gap, if any;
- counter-validation result;
- route hint or next owner, when deeper review or follow-up is needed;
- validation expected.

End with one Review Gate outcome:

- `review gate: satisfied` when findings or no-finding claims are specific,
  counter-validated, decision-useful, and ready for the user-visible verdict.
- `review gate: reopen` when material evidence is missing, contrary evidence
  weakens a finding, severity is uncertain, scope is too broad, or the visible
  verdict would not support a clear next decision.

The final verdict must support one clear next decision: accept, patch,
investigate, plan separately, or accept with a named residual risk.

## When to use

- The user asks for review of a concrete non-code or mixed artifact, workflow,
  AI resource, policy, plan, retained package, or bundle.
- The primary job is defect-first findings, not fixes.

## When not to use

- The user has already approved implementation or remediation work.
- The target is a dedicated code review of source, tests, scripts, build files,
  dependency files, or a code-focused diff; use `internal-code-review` instead.
- The request is mainly planning, brainstorming, execution, or file editing.
- The target is a specialist review where the user directly selected another
  owner.

## Validation

- Findings stay defect-first.
- Review surface selection matches the changed-path families.
- Review flow preserves compact context: prioritize diff and failing evidence first, then expand only when an evidence gap remains.
- Large evidence may be reported compactly, but each material finding still keeps severity, confidence, evidence gap, counter-validation result, and route or next owner.
- Review output carries findings, severity, confidence, evidence gap, counter-validation result, route or next owner, decision-usefulness result, and a Review Gate outcome before the final verdict.
- Route hints name likely specialist owners only when deeper review would change confidence, severity, owner, validation, or the next decision.
- Low-finding and no-finding reviews include enough evidence digest, decision trace, next action, and residual-risk context for the reader to decide whether to accept, patch, investigate, plan, or accept with named risk.
- The review cannot present analysis to the user until counter-validation confirms it or reopens material gaps.
- `internal-gateway-critical-master` is the only referenced skill used by this gateway; specialist references are route hints and must not be preloaded.
- The gateway stops before fixes.
