---
name: internal-skill-creator
description: Use when creating, materially revising, replacing, or retiring repository-owned skills under `.github/skills/`, including changes to scope, triggers, structure, or validation.
---

# Internal Skill Creator

## Core method

`/mattpocock-writing-great-skills` is the core method for skill authoring and
revision. Load it before drafting. Apply its relevant rules throughout the
change instead of repeating them here.

## Cross-skill notation

Prefix every cross-skill invocation with `/`.

Use the bare `skill-name` when a skill is only named or referenced, including
reference lists, identifiers, state labels, fixtures, scripts, and catalog
entries. Use `/skill-name` whenever an operational verb asks the agent to
load, run, use, invoke, delegate to, or route work to that skill. Apply this
distinction consistently to the six internal gateway skills covered by this
convention. Keep the target skill model-invocable; a called skill must not set
`disable-model-invocation: true`.

## Delegation admission

Before any delegation, the creator parent must fix the task-specific objective,
value gate, bounded evidence, constraints, write scope, expected output,
acceptance, validation, and budget. The work must be autonomous, verifiable,
and materially more useful to delegate than a trivial local operation. The
allowed creator classes and their `read`, `plan`, or `write` mapping are in
[`references/authoring-and-evaluation.md`](references/authoring-and-evaluation.md).

After that gate is complete, the parent may invoke `internal-luna-executor`
through `/internal-subagent-contract` with one `DelegationBrief` v1. The parent
retains trigger, boundary, policy, scope, retry choice, independent validation,
acceptance, semantic review, and closeout; it verifies one bound `WorkerResult`
v1 and caller-owned `VerificationReceipt` v1. Treat unobserved validation and
budget data as claims or unavailable evidence. When timeout, interruption,
executor unavailability, or missing terminal output prevents a worker payload,
record a caller-owned `LifecycleRecord` and create neither a synthetic
`WorkerResult` nor a receipt.

Keep a single command, one obvious edit, an unresolved policy, boundary,
authority, or acceptance decision, incomplete acceptance, and unverifiable
prose local or blocked. Default to one attempt. A corrective retry requires new
evidence and a concrete correction target; cosmetic, punctuation, prose-only,
and semantic disagreement do not reopen the worker.

Direct worker writes are limited to one exact declared artifact. The parent
reviews and accepts it. The worker does not edit the creator contract,
inventory, approval records, protected bundles, or broad directories.

## When to use

- The requested skill change affects repository-owned behavior or structure,
  including creating, materially revising, replacing, or retiring a skill.

## Local reference

Read `references/authoring-and-evaluation.md` when creating a skill, changing
its boundary or trigger, or selecting an evaluation branch.

## Workflow

### 1. Repository preflight

Read the target `SKILL.md`, the nearest competing skills, and the applicable
`AGENTS.md`. Inventory every existing sibling in the touched bundle:
`SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.
Distinguish real consumption from mere existence by mapping selectors,
cross-skill routing, validators, tests, inventory, and sync surfaces. Read
`.github/INVENTORY.md` when adding, retiring, renaming, or replacing a skill.

Completion criterion: the intended boundary, anti-scope, touched files, and
repository validation path are explicit.

### 2. Core authoring and revision

Load `/mattpocock-writing-great-skills` as the core method. Draft or revise the
smallest coherent bundle. Check invocation, description, information hierarchy,
retrieval quality, and predictability. Remove duplication, sediment, and no-ops;
revise the draft in place instead of only reporting findings.

Completion criterion: every applicable core rule is reflected in the draft,
and each retained local instruction has a repository-specific reason to exist.

### 3. Proportional evaluation

Read `references/authoring-and-evaluation.md`. Select the applicable evaluation
branches, including compatibility, lifecycle, propagation, and retirement when
material. Record skipped branches and reasons.

Use the reference's evaluation-selection matrix to choose evidence for each
change surface. Do not manufacture tests that assert instructional wording;
use parsed structure, executable consumers, public protocols, or concrete
evaluation cases instead.

Completion criterion: applicable branches have evidence; evidence, blockers,
and completion status are explicit.

### 4. Repository closure

1. Update `agents/openai.yaml` to match the revised skill purpose.
2. Run `python3 .github/scripts/validate_internal_skills.py --skill <name> --strict`.
3. Check routing fallout in nearby skills and agents.
4. For replacement or retirement work, remove hollow references and obsolete
   entrypoints, then record before/after line and word counts for the touched
   bundle.

Completion criterion: structural validation passes, routing fallout is resolved, and
before/after measurements are recorded.
