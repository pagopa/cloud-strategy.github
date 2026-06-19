---
name: internal-gateway-review
description: Use when repository-owned work needs same-conversation defect-first review, critical challenge of material remediation choices, and optional retained remediation planning before execution.
---

# Internal Gateway Review

## Referenced skills

- `internal-code-review`
- `internal-high-level-review`
- `internal-gateway-critical-master`
- `internal-gateway-writing-plans`
- `internal-agent-support-next-step`

Treat this section as an audit and routing index, not a preload bundle. Load a
referenced skill only when the domain, finding, blocker, or phase requires it.

Portable review orchestrator. Owns review scope, lens selection, findings
consolidation, critical support, and remediation-plan transition. It does not
apply fixes.

Before any user-visible verdict, run a lightweight internal check for evidence,
severity, false positives, contrary evidence, and scope narrowing. Load
`internal-gateway-critical-master` only for a material challenge. Revise or
reopen when the check exposes a material gap.

See `references/review-gate.md` for the review output contract and gate states.

## Token Discipline

Inspect diff and failing evidence first; avoid broad repository scans unless an
evidence gap requires one; never preload referenced skills; show at most 5
material findings unless exhaustive review is requested; summarize omitted
low-risk observations separately, not as findings.

## Review To Plan Transition

Before creating, accepting, or routing a remediation plan, keep the review
defect-first and map every original material finding: `id`, `status` (`planned`,
`deferred`, `rejected`, or `residual`), `reason`, `next owner`, and `validation
expected`.

If remediation steps cover less than 100% of material findings, label the
output `partial remediation plan` and keep residual, deferred, or rejected
findings visible. A retained mini-plan is a coverage-preserving handoff authored
by `internal-gateway-writing-plans`; its job is plan creation, not fixes. This
gateway does not choose the execution owner.

## When to use

- The user asks for review of a concrete artifact, diff, workflow, or bundle.
- The primary job is defect-first findings and remediation planning, not fixes.

## Validation

- Findings stay defect-first.
- Review flow preserves compact context: prioritize diff and failing evidence first, then expand only when an evidence gap remains.
- Review output carries findings, severity, confidence, evidence gap, counter-validation result, route or next owner, and a Review Gate outcome before the final verdict.
- The review cannot present analysis to the user until counter-validation confirms it or reopens material gaps.
- Remediation-plan transitions preserve a 100% material-finding coverage map or explicitly declare a `partial remediation plan`.
- Retained remediation plans are authored by `internal-gateway-writing-plans` and preserve the coverage map.
- The gateway stops before fixes.
