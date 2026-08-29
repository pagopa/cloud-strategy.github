---
name: internal-skill-creator
description: Use when creating, materially revising, replacing, or retiring repository-owned skills under `.github/skills/`, including changes to scope, triggers, structure, or validation.
---

# Internal Skill Creator

## Core method

`/mattpocock-writing-for-agents` is the core method for skill authoring and
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
its boundary or trigger, or selecting an evaluation branch. Read
`references/cache-and-token-efficiency.md` when creating or materially
revising a bundle so the always-loaded prefix stays cache-stable and within
progressive-disclosure budgets.

## Workflow

### 1. Repository preflight

Read the target `SKILL.md`, the nearest competing skills, and the applicable
`AGENTS.md`. Inventory every existing sibling in the touched bundle:
`SKILL.md`, `references/`, `scripts/`, `assets/`, `agents/openai.yaml`, and
the paired `.github/agents/<name>.agent.md` when one exists.
Distinguish real consumption from mere existence by mapping selectors,
cross-skill routing, validators, tests, inventory, and sync surfaces. Read
`.github/INVENTORY.md` when adding, retiring, renaming, or replacing a skill.

Completion criterion: the intended boundary, anti-scope, touched files, and
repository validation path are explicit.

### 2. Core authoring and revision

Load `/mattpocock-writing-for-agents` as the core method. Draft or revise the
smallest coherent bundle. Check invocation, description, information hierarchy,
retrieval quality, and predictability. Remove duplication, sediment, and no-ops;
revise the draft in place instead of only reporting findings. Apply the
portable frontmatter rules and route invocation policy to agents/openai.yaml.
Apply the cache-stability rules, progressive-disclosure budgets, and sediment
review in
[`references/cache-and-token-efficiency.md`](references/cache-and-token-efficiency.md):
no volatile content may enter an always-loaded surface.

Completion criterion: every applicable core rule is reflected in the draft,
each retained local instruction has a repository-specific reason to exist, and
the always-loaded surfaces are byte-stable and within budget.

### 3. Proportional evaluation

Read `references/authoring-and-evaluation.md`. Select the applicable evaluation
branches, including compatibility, lifecycle, propagation, and retirement when
material. Record skipped branches and reasons. Apply the evaluation-harness requirements in `references/authoring-and-evaluation.md`.

Use the reference's evaluation-selection matrix to choose evidence for each
change surface. Do not manufacture tests that assert instructional wording;
use parsed structure, executable consumers, public protocols, or concrete
evaluation cases instead.

Completion criterion: applicable branches have evidence; evidence, blockers,
and completion status are explicit.

### 4. Repository closure

1. Sync every public projection of the revised contract when the SKILL.md
   purpose, report, or output contract changes: `agents/openai.yaml` and, when
   a paired `.github/agents/<name>.agent.md` exists, its Output section. A
   projection must not require output fields or sections that SKILL.md
   excludes from chat.
2. Validate the revised bundle from the bundle itself: parse `SKILL.md`
   frontmatter, confirm declared siblings exist, and run any bundle-local
   tests. Do not require a host-repository catalog dispatcher.
3. Check routing fallout in nearby skills and agents.
4. For replacement or retirement work, remove hollow references and obsolete
   entrypoints. For any material revision, record before/after line, word, and
   estimated token counts for the always-loaded surfaces, and confirm no
   volatile content entered a cached prefix.
5. Record the runtime propagation limit: a session started before a contract
   change keeps the previous skill snapshot in memory. Do not validate the new
   contract from an in-flight session; restart or use a newly started session
   to prove the new behavior.

Completion criterion: structural validation passes, routing fallout is resolved, and
before/after measurements are recorded.
