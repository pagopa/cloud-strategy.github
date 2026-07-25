---
name: internal-review-ai-resources
description: Use when reviewing repository-owned AI resources, bundle siblings, catalog workflows, or retained AI review packages before deciding keep, patch, split, compress, or retire actions.
---

# Internal Review AI Resources

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `internal-copilot-audit`: on-demand drift lens for overlap, hollow references, stale contracts, naming drift, and governance drift.

Use this skill as the qualitative review owner for repository-owned AI
resources and retained AI review packages. It owns profile selection,
evidence-first qualitative review, lifecycle checks, and proportional
reporting. Keep `internal-copilot-audit` as the drift lens instead of copying
its audit order here.

## When to use

- Review one AI asset, a bundle root, several catalog folders, or a retained
  review package under `tmp/`.
- Decide whether to keep, wrap, patch, split, merge, move, retire, compress,
  automate, or review later.
- Check how AI resources are consumed across prompts, agents, skills,
  validators, tests, inventory, and sync helpers.
- Evaluate lifecycle posture such as compatibility, propagation, periodic
  review, and retirement readiness.

## When not to use

- Use `internal-copilot-audit` when the primary goal is overlap, hollow
  references, stale contracts, or governance drift findings.
- Use the owning delivery lane when the task is already approved
  implementation instead of analysis.
- Use deterministic validators and tests for enforcement; do not turn this
  skill into a validator replacement.
- Do not review unrelated application or infrastructure files unless an
  in-scope AI resource references them.

## Reviewable families

Reviewable families: see `references/review-profiles.md` 'Family coverage baseline'.

## Review profiles

Load `references/review-profiles.md` when choosing scope or escalating beyond
one file.

- `focused`: one file or one narrow resource plus its direct evidence path.
- `bundle`: one bundle owner plus existing siblings and local propagation
  paths.
- `catalog`: cross-family review of the repository AI catalog and its
  validators.
- `retained-report`: review an existing retained report package against live
  repository evidence.

## Evidence-first workflow

1. Resolve the target to the smallest correct profile. For skill bundle
   targets, keep the bundle root and existing siblings in scope.
2. Read `AGENTS.md`, `.github/copilot-instructions.md`, the target owner, and
   the nearest validators or tests.
3. Build a local consumption map: who selects the resource, what it
   references, which validators prove it, and what propagation surfaces must
   stay aligned.
4. Load `references/review-checklist.md` for lifecycle, flow, context,
   validation, sync, and propagation checks sized to the chosen profile.
5. Load `internal-copilot-audit` only when the review needs overlap,
   hollow-reference, stale-contract, naming, or governance-drift findings.
6. Load `references/report-contract.md` before writing the final review so
   evidence labels, decision vocabulary, and completeness checks stay
   proportional to the profile.
7. Use `references/review-usefulness-replay-fixture.md` as the illustrative
   output shape when changing the decision-usefulness behavior of AI-resource reviews.

## Core review rules

- When this skill reviews itself, name the rationalization risk explicitly and prefer evidence from external consumers over self-cited compliance.
- Stay analysis-only unless the user explicitly changes lanes into delivery.
- Keep one generic review lane across prompts, skills, agents, catalog
  helpers, and retained packages; do not split the owner by resource family
  unless evidence shows the boundary is broken.
- Treat bundle siblings as default in-scope evidence for bundle reviews. If a
  sibling is intentionally out of scope, say so explicitly.
- Distinguish consumption from mere existence. Prefer findings backed by agent
  routing, prompt references, validators, sync catalogs, or tests.
- Prefer the smallest evidence path that can prove a claim. Read more only when
  the next claim cannot be supported locally.
- Keep deterministic controls in validators and tests. Use this skill for
  qualitative judgment, not hidden enforcement.
- When a recommendation would change propagation, include the affected
  inventory, sync, validator, and test surfaces in scope before finalizing the
  recommendation.

## Bundle coverage rules

Bundle coverage rules: see `references/review-profiles.md` 'bundle minimum evidence pass'. Checked surfaces with no defect belong in the evidence digest or decision trace, not as findings.

## Output

- Chat projection: see `references/report-contract.md` 'Chat projection'.
- Retained output: see `references/report-contract.md` 'Retained output'.

The review output should always be decision-useful and include an explicit
no-findings result when no material findings exist.

## Validation

- The selected profile matches the target and escalation rules in
  `references/review-profiles.md`.
- The review covers the relevant resource families for the chosen profile.
- Bundle reviews include existing `references/`, `scripts/`, `assets/`, and
  `agents/openai.yaml`, or explicitly mark intentional non-action.
- Bundle reviews distinguish coverage from findings and compress checked-clean
  surfaces into evidence digest or decision trace.
- Lifecycle, compatibility, propagation, periodic review, and retirement checks
  are available through `references/review-checklist.md`.
- `internal-copilot-audit` is used as a named drift lens when those findings
  are needed, not copied inline.
- The final output follows `references/report-contract.md` and stays
  proportional to the chosen profile.
- Decision-usefulness contract changes preserve the behavior captured in
  `references/review-usefulness-replay-fixture.md` illustrative output shape.
