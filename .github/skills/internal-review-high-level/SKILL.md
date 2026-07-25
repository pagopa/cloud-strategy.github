---
name: internal-review-high-level
description: Use when a task needs systems-fit evidence about architecture, workflow, cross-cutting impact, blind spots, operational context, or an orientation map of unfamiliar code.
---

# Internal Review High Level

This skill owns systems-fit review and architecture/orientation only. It is an
evidence-first reviewer, not a remediation owner. Keep cross-owner routes
recommendation-only. Do not delegate.

## When to use

- Review whether a change fits its architecture, workflow, ownership, and
  operational context.
- Check cross-cutting impact, blind spots, scope drift, and merge risk.
- Build an evidence-based orientation map of unfamiliar code.

## When not to use

- Use `internal-review-code` for line-level defects, language anti-patterns,
  tests, and file-specific findings.
- Use `internal-gateway-critical-master` for explicit pressure testing rather
  than evidence-first systems review.
- Route security-specific gaps through the closest existing owner and state the
  missing specialized-owner gap when no promoted security owner exists.
- Do not turn advisory architecture notes into mandatory changes without
  evidence, and do not create new context or glossary structures as a review
  side effect.

## Branch selection

### Systems-fit review

Use this branch for systems-level findings, workflow impact, architecture fit,
blind spots, scope drift, or merge-readiness evidence. Load
`references/analysis-dimensions.md`, `references/review-lenses.md`, and
`references/scope-drift.md` only when their evidence is needed. Report findings
with the single severity/confidence vocabulary in `review-lenses.md`.

### Architecture and orientation

Use this branch for architecture-fit questions or an orientation map of an
unfamiliar area. Load only the architecture and codebase-orientation portions
of `references/analysis-dimensions.md`. Keep the result descriptive unless
concrete evidence supports a systems finding.

## Compatibility-only plan audit

Use `references/plan-completion-audit.md` only for an explicit retained-plan
audit request or an existing execution-owner compatibility path. Plan audit is
not a primary trigger, and ownership migration is outside this change.

## Evidence-first workflow

1. Resolve the target, declared intent, anti-scope, and nearest owner.
2. Select exactly one branch and load only its referenced evidence.
3. Read the target and immediate dependencies; map boundaries and callers.
4. Test contrary explanations and record concrete evidence gaps.
5. Project the matching finding or orientation output.
6. Validate every claim, route code defects to `internal-review-code`, and keep
   recommendations non-binding.

## Systems-fit output

Present findings by severity, then evidence gaps, blind spots, architecture
notes, and a short summary. Every actionable finding must cite concrete file
and line evidence, explain the causal layer, and name a minimal recommendation-
only route. Speculative concerns are evidence gaps, not actionable findings.

## Architecture and orientation output

For an orientation request, provide the target area, domain vocabulary, module
map, flow map, boundary notes, and uncertainty. Name caller or entrypoint
evidence and validation gaps. Do not include review sections in an
orientation-only response.

## Completion boundary

Keep no-findings, merge-readiness, and complete-review claims behind
`superpowers-verification-before-completion`.
