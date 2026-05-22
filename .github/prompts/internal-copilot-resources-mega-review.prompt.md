---
name: "internal-copilot-resources-mega-review"
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

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
- [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)
- [.github/skills/internal-copilot-audit/SKILL.md](../skills/internal-copilot-audit/SKILL.md)
- [.github/skills/internal-agent-creator/SKILL.md](../skills/internal-agent-creator/SKILL.md)
- [.github/skills/internal-skill-creator/SKILL.md](../skills/internal-skill-creator/SKILL.md)
- [.github/skills/internal-copilot-instructions-creator/SKILL.md](../skills/internal-copilot-instructions-creator/SKILL.md)

Load additional repository skills only when the target resource or its
references require their owner rules. Do not load every skill only because it
exists.

## Mission

Run an evidence-based review of repository-owned AI resources and their
referenced local assets.

The review must explain:

- what each relevant resource owns
- how it is activated or consumed
- which local files it references
- how it behaves inside the repository operational flow
- which overlaps, gaps, stale references, and flow risks matter
- what should be kept, wrapped, revised, split, merged, moved, retired, created,
  compressed, automated, or reviewed later

The review is analysis-only. Do not modify the reviewed resources. If retained
analysis is needed, write only under `tmp/`.

Do not name vendor-specific reasoning engines or compare them. Review consumer
surfaces, contracts, and repository behavior instead.

## Target Resolution

Accept any of these inputs in `Review target`:

- one concrete resource path, such as `AGENTS.md`,
  `.github/agents/<name>.agent.md`, `.github/prompts/<name>.prompt.md`,
  `.github/instructions/<name>.instructions.md`, or
  `.github/skills/<name>/SKILL.md`
- one or more folders, such as `.github/agents/`, `.github/skills/`,
  `.github/instructions/`, `.github/prompts/`, `.github/scripts/`, or
  AI-catalog test folders under `tests/`
- the full AI catalog, meaning `AGENTS.md`, `.github/copilot-*.md`,
  `.github/INVENTORY.md`, `.github/agents/`, `.github/instructions/`,
  `.github/prompts/`, `.github/skills/`, AI catalog validation or sync scripts
  under `.github/scripts/`, and tests that validate those resources
- an existing retained report package under `tmp/`, in which case review the
  report against current repository evidence instead of treating it as policy

If a target is ambiguous, resolve obvious repository paths first. Ask only when
the target cannot be resolved safely from filesystem evidence.

## Resource Families In Scope

Review these families when they are in the target or referenced by it:

- `AGENTS.md`
- `.github/copilot-instructions.md` and related `.github/copilot-*.md` files
- `.github/INVENTORY.md`
- `.github/agents/*.agent.md`
- `.github/instructions/*.instructions.md`
- `.github/prompts/*.prompt.md`
- `.github/skills/**/SKILL.md`
- skill-local `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`
- AI catalog validators, sync helpers, and inventory scripts under
  `.github/scripts/`
- tests and fixtures that validate AI catalog behavior, prompt contracts,
  inventory, sync, token-risk checks, or validation entrypoints
- local docs, templates, manifests, or retained reports that are explicitly
  referenced by an in-scope resource

Do not expand into unrelated application, infrastructure, or documentation files
unless an in-scope AI resource references them or a validator requires them.

## Mandatory Control Pass

Before judging quality:

1. Read `AGENTS.md` and `.github/copilot-instructions.md`.
2. Read every scoped instruction whose `applyTo` metadata matches reviewed
   Markdown, script, YAML, or other target paths.
3. Resolve the target as a single resource, folder set, full catalog, or retained
   report package.
4. Verify which in-scope resource families exist on disk.
5. Build a local reference graph from frontmatter, Markdown links, declared
   skills, paired agents, `references/`, `scripts/`, `assets/`, and validator
   references.
6. Map tests and validation entrypoints that cover the target before judging
   whether a resource is safe to revise, merge, move, retire, or keep.
7. Load only the repository skills that own a relevant decision boundary.
8. Compare thin wrappers, core skills, prompt entrypoints, scoped instructions,
   sync helpers, and tests by role before calling anything duplicated.
9. Keep a running list of unproven claims and place them in low-evidence or open
   questions sections.
10. Decide whether the output can stay in chat or needs a retained report under
    `tmp/`.

## Flow Behavior Review

For every material resource or resource group, evaluate how it behaves inside
the repository flow:

- Activation: what causes it to load or be selected.
- Owner: which file owns route, policy, reusable procedure, deep detail,
  validation, sync, or reporting.
- Phase behavior: how it supports `plan`, `execute`, `apply-plan`, `review`, or
  handoff decisions.
- References: which local files it asks the operator to read, load, run, or keep
  aligned.
- Boundary: what it must not own, and which adjacent owner should take over.
- Evidence path: which validator, script, test, or manual check proves the
  resource still works.
- Failure behavior: what happens when a reference is missing, a target is
  ambiguous, a validator fails, or the selected owner no longer fits.
- Context cost: what is always visible, what should be lazy-loaded, and what can
  be compressed without losing routing clarity.
- Propagation: whether changes must update inventory, sync scripts, validators,
  paired agents, paired skills, scoped instructions, or retained reports.

## Review Questions

Use these as an internal checklist, not as a required final outline.

Agents:

- Are the existing agents necessary?
- Which agents are redundant, too broad, too narrow, or missing?
- Does each agent have a distinct route, boundary, tool contract, and output
  expectation?
- Does a wrapper stay thin when a core skill owns reusable procedure?
- Should any agent behavior move into a skill, prompt, or scoped instruction?
- Are handoffs and stop conditions explicit and user-visible?
- Are route names and agent names clear enough for selection?

Instructions:

- Are instructions partitioned correctly?
- Does `applyTo` match the intended path family without excess co-loading?
- Are some instructions never activated or too generic?
- Do instructions contain only path-scoped rules that should auto-apply?
- Are workflow depth and optional expertise kept in skills or prompts?
- Do instructions avoid duplicating repository-wide policy?

Skills:

- Are skills partitioned correctly?
- Does each skill have a clear trigger, smallest credible owner, and useful
  boundary?
- Is each skill useful, too large, too small, redundant, or stale?
- Is each skill optimized for context cost and token ROI?
- Should any skills be merged, retired, split, or renamed?
- Should any skills become instructions or prompts?
- Are high-ROI skills missing?
- Do skills connect cleanly to agents, prompts, instructions, and validation?
- Are references, scripts, and assets inside the skill bundle justified by
  repeated need?
- Do paired agents and skills agree on route, procedure, and deep-detail split?

Prompts:

- Are prompts useful, too many, or too few?
- Does each prompt have clear inputs, agent owner, constraints, and expected
  output?
- Is the prompt reusable across resource families without hardcoding one
  consumer surface?
- Does it collect enough target, depth, and constraint information to avoid
  hidden assumptions?
- Does it define versioning or compatibility expectations when those matter?
- Should any prompt logic become a skill, instruction, or validator instead?

Bridge and catalog files:

- Do `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md`
  agree on precedence, rule placement, and live catalog shape?
- Are exact catalog paths kept in inventory instead of duplicated in bridge
  files?
- Are repository-wide rules stable enough for always-visible guidance?
- Is there a clear map, decision log, or update guide for maintaining the AI
  catalog without breaking routing or validation?

Scripts and validators:

- Are scripts still necessary, simple, fast, documented, and idempotent?
- Do scripts validate catalog shape, references, frontmatter, inventory, sync, or
  token-risk claims that humans would otherwise miss?
- Do scripts have adequate error handling and safe local behavior?
- Are validation entrypoints discoverable from `Makefile` or `.github/scripts/`?
- Can scripts generate inventory, maps, reports, or validation evidence?
- Which automation would immediately reduce drift with the smallest maintenance
  cost?

Tests:

- Which tests cover agents, skills, instructions, prompts, inventory, sync,
  token-risk checks, and prompt contracts?
- Are tests focused, fast, deterministic, and tied to the catalog contracts they
  protect?
- Are there missing tests for high-risk routing, frontmatter, reference graphs,
  or retained-report output contracts?
- Do tests fail loudly when a resource is renamed, retired, moved, or left out of
  inventory?
- Are fixtures clear enough to explain the expected catalog behavior?

Referenced assets:

- Are linked references present, local, and still useful?
- Do local references carry deep detail that should not be copied into wrapper
  agents or top-level skills?
- Are scripts or assets still needed by the resource that references them?

Context economy:

- What gets loaded too often?
- What should be lazy-loaded?
- What belongs in minimal always-visible guidance?
- What belongs in on-demand skills, prompt files, scoped instructions, docs, or
  tests?
- Which expensive overlaps should be compressed only after role differences are
  proven?

Productivity:

- What truly accelerates analysis, implementation, review, and verification?
- What creates friction or requires too much maintenance?
- Where is the repository over-engineered or under-invested?
- Which five quick interventions would deliver the highest ROI?
- Which three things should stop and which three should start?

## Evidence Standard

Use these evidence labels:

- `HIGH`: supported by concrete files and direct comparison.
- `MEDIUM`: supported by repeated patterns observed in repository evidence.
- `LOW`: plausible but not fully proven.
- `VERIFY`: requires manual confirmation or a check that was not run.

Rules:

- Do not recommend `MERGE`, `MOVE`, `SPLIT`, `RETIRE`, or `CREATE` with `LOW`
  evidence.
- For low confidence, use `REVIEW` or `VERIFY`.
- Every strong recommendation must cite at least one real file.
- Separate `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, and `UNKNOWN`.
- Do not turn an `ASSUMPTION` or `UNKNOWN` into a strong recommendation.

## Overlap Classification

Do not call resources duplicated only because they share terms or topics. Compare
actual role, activation, audience, phase, abstraction level, context cost,
validation, and repository hierarchy.

Classify every overlap as one of:

- `REAL DUPLICATION`
- `ACCEPTABLE OVERLAP`
- `INTENTIONAL OVERLAP`
- `VERIFY`

When an imported or external-pattern resource overlaps with an `internal-*`
resource, use this decision logic:

- `KEEP`: distinct value and no harmful conflict.
- `WRAP`: useful external value needs repository-owned boundary control.
- `REVIEW/RETIRE`: current value is unclear, stale, conflicting, or replaceable.

## Decision Criteria

Evaluate relevant resources with these criteria:

- necessity
- uniqueness
- route clarity
- activation timing
- owner boundary
- referenced-resource health
- context cost and lazy-load fit
- maintainability
- composability
- test coverage and validation path
- sync and propagation impact
- user productivity
- safety and least privilege
- alignment with `AGENTS.md` and `.github/copilot-instructions.md`
- evidence quality

## Output Location Rules

If the target is one small resource and `Output preference` does not require a
file, answer in chat.

If the target spans multiple folders, the full AI catalog, or an existing
retained report package, write a split retained report under:

- `tmp/superpowers/ai-resource-mega-review/`

For a fresh retained report, create:

- `01-executive-summary.md`
- `02-target-and-coverage.md`
- `03-resource-map.md`
- `04-flow-behavior.md`
- `05-findings-and-decisions.md`
- `06-tests-and-validation.md`
- `07-recommendations-and-roadmap.md`
- `open-questions.md`

If the folder already exists, preserve prior analysis and add an addendum unless
the user explicitly asks to replace it.

## Required Output Structure

Use this structure in chat or across the retained report files.

### 1. Executive Summary

- Maximum 10 lines.
- State the actual condition of the target: healthy, coherent but improvable,
  redundant, fragile, unclear, stale, or blocked by missing evidence.

### 2. Target And Coverage

- State resolved paths.
- State included and excluded resource families.
- State which referenced resources were followed.

### 3. Repository Hierarchy

- Summarize the effective precedence between `AGENTS.md`,
  `.github/copilot-instructions.md`, scoped instructions, agents, skills,
  prompts, scripts, inventory, and referenced docs.

### 4. Resource Map

- Table: `Resource | Family | Owner role | Activation | Key references | Validation`.

### 5. Flow Behavior

- Explain how the target behaves through planning, execution, review, handoff,
  failure, validation, and propagation.
- Include the highest-risk flow mismatch, if any.

### 6. Test And Validation Coverage

- State which tests, validators, lint checks, or manual checks cover the target.
- Identify missing tests or weak assertions for high-risk AI catalog behavior.
- Distinguish validation that exists from validation that was not run.

### 7. Main Diagnosis

- Split into what works, what is redundant, what is fragile, what costs too much
  context, what blocks productivity, what lacks test coverage, and what is
  missing.
- Keep each subsection to the highest-signal points.

### 8. Main Findings

- Group by severity or priority.
- For each finding include `Evidence`, `Problem`, `Impact`, `Recommendation`,
  and `Confidence`.

### 9. Decision Table

- Table: `Area | Resource | Status | Evidence | Problem | Decision | Priority`.
- Allowed statuses: `KEEP`, `WRAP`, `REVISE`, `COMPRESS`, `SPLIT`, `MERGE`,
  `MOVE`, `RENAME`, `RETIRE`, `CREATE`, `AUTOMATE`, `REVIEW`.
- Allowed priorities: `P0`, `P1`, `P2`, `P3`.

### 10. Overlaps And Boundaries

- Table: `Resources involved | Type | Evidence | Assessment | Proposed action`.
- Use the overlap classifications exactly.

### 11. Recommendations, Roadmap, And Target Rules

- Split into `Do now`, `Do later`, and `Do not do now`.
- `Do now` may include only `HIGH` or `MEDIUM` evidence actions.
- Include a non-binding roadmap split into `Cleanup`, `Rationalization`,
  `Automation`, `Governance`, and `Evolution` when the target is broad enough.
- Include target architecture differences versus the current state when the
  evidence supports a better structure.
- Include a future-rule table `Type | When to create it | When to avoid it` for
  agent, skill, instruction, prompt, script, test, and doc when the review makes
  artifact-placement decisions.

### 12. Quick Wins And Automation

- Maximum 10 items.
- Table: `Action | Evidence | Impact | Effort | First check`.

### 13. Low-Evidence Items And Open Questions

- Keep `LOW` and `VERIFY` items separate from strong recommendations.
- Use: `Item | Why uncertain | What to verify`.

### 14. Final Critique

- Maximum 10 lines.
- State what works, what is overcomplicated, what slows delivery, what is risky,
  and the best next step.

## Completeness Pass

Before the final answer:

1. Re-open any retained report file written under `tmp/`.
2. Confirm the requested target was fully resolved or explicitly marked
   unresolved.
3. Confirm every in-scope family was either reviewed or marked not present.
4. Confirm all referenced local resources that materially affect the decision
   were checked or marked `VERIFY`.
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
