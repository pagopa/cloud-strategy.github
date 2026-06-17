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

Portable review orchestrator. This skill owns review scope, lens selection,
findings consolidation, critical support, and remediation-plan transition. It
does not apply fixes.

See `references/review-gate.md` for the review output contract and gate states.

## When to use

- The user asks for review of a concrete artifact, diff, workflow, or bundle.
- The primary job is defect-first findings and remediation planning, not fixes.

## Validation

- Findings stay defect-first.
- Review flow preserves compact context: prioritize diff and failing evidence first, then expand only when an evidence gap remains.
- Review output carries findings, severity, confidence, evidence gap, route or next owner, and a Review Gate outcome before the final verdict.
- Retained remediation plans are authored by `internal-gateway-writing-plans`.
- The gateway stops before fixes.
