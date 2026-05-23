---
name: "internal-review-ai-resources"
agent: "internal-gateway-operational-flow"
description: "Review repository-owned AI resources, referenced assets, and flow behavior across AGENTS.md and .github"
argument-hint: "Target one file, one or more folders, the full AI catalog, or an existing retained report package"
---

<!-- markdownlint-disable-file MD041 -->

Primary goal:
${input:goal:Describe why this review is needed and what decision it must support}

Review target:
${input:target:List one resource, several folders, the full AI catalog, or an existing retained report package}

Consumer surfaces:
${input:consumers:List relevant consumers such as GitHub Copilot, Codex, local sync, or write infer from repository evidence}

Known local assumptions or concerns:
${input:assumptions:List internal wrappers, imported-resource posture, known drift, prior findings, or write infer from repository evidence}

Desired depth:
${input:depth:Choose concise, detailed, or exhaustive; default to detailed when unsure}

Constraints and exclusions:
${input:constraints:List no-touch areas, rollout constraints, evidence limits, or explicit exclusions}

Output preference:
${input:output:Write chat-only, retained report under tmp/, or infer from target size}

## Source Loading Order

Always load:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- the resolved target path or paths
- every scoped instruction whose `applyTo` matches an in-scope target path

Load only when needed:

- [.github/INVENTORY.md](../INVENTORY.md) for catalog-wide naming, discovery,
  sync, or propagation claims
- [INTERNAL_CONTRACT.md](../../INTERNAL_CONTRACT.md) for repo-wide contract or
  governance disagreements
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
  and [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)
  for flow, phase, handoff, completion, or retained-plan claims
- [.github/skills/internal-copilot-audit/SKILL.md](../skills/internal-copilot-audit/SKILL.md)
  for overlap, hollow-reference, governance-drift, bundle-health, or token-risk
  decisions
- [.github/skills/internal-agent-creator/SKILL.md](../skills/internal-agent-creator/SKILL.md),
  [.github/skills/internal-skill-creator/SKILL.md](../skills/internal-skill-creator/SKILL.md),
  and [.github/skills/internal-copilot-instructions-creator/SKILL.md](../skills/internal-copilot-instructions-creator/SKILL.md)
  only when the recommendation would create, split, retire, or replace those
  resource families

Load optional owner skills only when the target or a live decision boundary
requires them. Do not load every skill only because it exists.

Use `LESSONS_LEARNED.md` only when it is explicitly in the target, referenced by
an in-scope resource, or needed to verify a retained-learning claim. Treat it as
non-canonical retained evidence until codified in the smallest valid owner.

## Language Rules

- Write the final analysis and summary in the language of the current chat.
- If the current chat language is ambiguous or mixed, prefer Italian.
- Keep file paths, enum values, evidence labels, status labels, and command names
  exactly as requested.

## Mission

Run an evidence-based review of repository-owned AI resources and their
referenced local assets.

The review is analysis-only. Do not modify the reviewed resources. If retained
analysis is needed, write only under `tmp/`.

Do not name vendor-specific reasoning engines or compare them. Review consumer
surfaces, contracts, repository behavior, and validation paths instead.

Do not produce an encyclopedic review. Include only real problems, important
tradeoffs, recommended decisions, blocking uncertainties, and high-ROI quick
wins.

## Target Resolution

Accept any of these inputs in `Review target`:

- one concrete resource path
- one or more relevant folders
- the full AI catalog
- an existing retained report package under `tmp/`

If a target is ambiguous, resolve obvious repository paths first. Ask only when
the target cannot be resolved safely from filesystem evidence.

When the target is `.github/skills/<name>/` or `.github/skills/<name>/SKILL.md`,
resolve the owning skill bundle and keep its bundle siblings (`references/`,
`scripts/`, `assets/`, and `agents/openai.yaml`) in scope unless explicitly
excluded.

## Scope Rules

Review only the target families and direct references needed to support the
decision.

For skill bundles, treat existing bundle siblings as default in-scope coverage
unless explicitly excluded.

For skill bundles, confirm each existing bundle sibling was reviewed or marked
intentional non-action in the source-item coverage matrix.

Do not expand into unrelated application, infrastructure, or documentation files
unless an in-scope AI resource references them or a validator requires them.

## Token And Read Discipline

- Start with the smallest evidence pass that can confirm or disconfirm the main
  concern.
- Read the target, controlling owner, nearest validator, and direct references
  before broad catalog surfaces.
- Prefer exact path checks, compact tables, and delta notes over long narrative
  taxonomies.
- Keep a compact source-item coverage matrix instead of rereading the same
  surfaces.
- Expand only when the evidence conflicts, a validator pulls more files in, or a
  cross-family decision cannot be made locally.

## Review Loop

1. Resolve the target and smallest credible in-scope family set.
2. Identify owner, activation path, usage proof, and nearest validator or test.
3. Build the direct reference graph from frontmatter, local links, declared
   skills, paired agents, bundle siblings, scripts, assets, and validator
   references.
4. Check bundle completeness, validation coverage, propagation impact, context
   cost, and token ROI.
5. Keep unproven claims in `LOW` or `VERIFY`, not as strong structural
   recommendations.
6. Use the smallest output shape that supports the decision before writing.

## Core Review Lenses

Check only the lenses that the target actually needs:

- ownership and boundary clarity
- activation and usage proof
- reference health and bundle completeness
- validation, sync, and propagation coverage
- context cost, lazy-load fit, and token ROI
- flow behavior when plan, execute, apply-plan, review, or handoff semantics are
  part of the target

When relevant to the target family, also check these local questions:

- Agents: route clarity, thin-wrapper discipline, tool contract, and stop
  conditions
- Instructions: `applyTo` precision, path-scoped fit, and overlap justification
- Skills: trigger clarity, bundle sibling necessity, paired-wrapper alignment,
  and lazy-load fit
- Prompts: input clarity, output calibration, owner routing, and preload budget
- Scripts, validators, and tests: discoverability, coverage, idempotence, and
  failure signal quality

## Evidence And Decision Rules

Use these evidence labels:

- `HIGH`: supported by concrete files and direct comparison.
- `MEDIUM`: supported by repeated patterns observed in repository evidence.
- `LOW`: plausible but not fully proven.
- `VERIFY`: requires manual confirmation or a check that was not run.

Rules:

- Do not recommend `MERGE`, `MOVE`, `SPLIT`, `RETIRE`, or `CREATE` with `LOW`
  evidence.
- For low confidence, use `REVIEW` or `VERIFY`.
- Every structural recommendation must cite at least one real file and one
  `First check` that would confirm or disconfirm the change.
- Separate `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, and `UNKNOWN`.

Classify overlaps only as:

- `REAL DUPLICATION`
- `ACCEPTABLE OVERLAP`
- `INTENTIONAL OVERLAP`
- `VERIFY`

When an imported or external-pattern resource overlaps with an `internal-*`
resource, use `KEEP`, `WRAP`, or `REVIEW/RETIRE` based on actual role,
activation, context cost, and repository hierarchy.

## Output Calibration

Use the smallest output shape that supports the decision.

- One resource or one narrow folder: answer in chat unless retained output was
  explicitly requested.
- One medium target with retained output: write one concise Markdown file under
  `tmp/`.
- Multiple folders, full catalog, or an existing retained report package: write a
  split retained report under `tmp/superpowers/ai-resource-mega-review/`.

If the retained folder already exists, preserve prior analysis and add only the
delta or correction needed unless the user explicitly asks to replace it.

## Required Output Contract

Every output must include these parts in the smallest workable form:

1. `Executive summary`: the actual condition of the target in at most 10 lines.
2. `Target and coverage`: resolved paths, included families, exclusions, and a
   source-item coverage matrix with `Item | Why in scope | Evidence | State`.
3. `Main findings`: only high-signal problems, tradeoffs, and blocking
   uncertainties.
4. `Decision table`: `Resource | Status | Why | First check`.
5. `Validation and open questions`: validators run, validators not run, and any
   unresolved `LOW` or `VERIFY` items.

Allowed statuses: `KEEP`, `WRAP`, `REVISE`, `COMPRESS`, `SPLIT`, `MERGE`,
`MOVE`, `RENAME`, `RETIRE`, `CREATE`, `AUTOMATE`, `REVIEW`.

If you use a split retained package, create only the files that carry distinct
information from this compact set:

- `01-executive-summary.md`
- `02-target-and-coverage.md`
- `03-resource-map.md`
- `04-flow-behavior.md`
- `05-findings-and-decisions.md`
- `06-tests-and-validation.md`
- `07-recommendations-and-roadmap.md`
- `open-questions.md`

Do not create filler sections or duplicate the same finding across files.

## Completeness Pass

Before the final answer:

1. Re-open any retained report file written under `tmp/`.
2. Confirm the requested target was fully resolved or explicitly marked
   unresolved.
3. Confirm every in-scope family was either reviewed, marked not present, or
   marked intentional non-action.
4. Confirm every strong recommendation cites real file evidence, a `First check`,
   and the nearest validator or explicit validation gap.
  For skill bundles, confirm each existing bundle sibling was reviewed or
  explicitly marked out of scope, absent, or `VERIFY`.
5. Confirm test and validation coverage was reviewed for every target where
   tests or validators exist.
6. Confirm skill coverage includes partitioning, triggers, usefulness, size,
   redundancy, token ROI, merge or retirement candidates, conversion to
   instructions or prompts, missing high-ROI skills, agent linkage, and
   validation linkage.
7. Confirm prompt coverage includes usefulness, count, reuse value, inputs,
   outputs, constraints, compatibility expectations, and conversion candidates.
8. Confirm script coverage includes necessity, simplicity, speed, documentation,
   idempotence, error handling, validation value, and automation opportunities.
9. Confirm every strong recommendation has `HIGH` or `MEDIUM` evidence and cites
   a real file.
10. Confirm no destructive decision uses `LOW` evidence.
11. Confirm every overlap was checked against wrapper, core-skill, prompt,
   scoped-instruction, and sync-helper roles before being classified as real
   duplication.
12. Confirm flow behavior was reviewed, not only static file content.
13. Confirm no reviewed resource was modified.
14. Report validation commands run, validation gaps, and residual risk.

Final response must include:

- active phase and owner
- reviewed target
- output location, if any
- top decisions or findings
- validation evidence or validation gap
- recommended next step
