# Knowledge Scope

Use this reference to decide **what the skill may touch** before any drafting starts. It owns mode resolution, target discovery, the write allowlist, the preflight plan, and the completion report. It never decides document structure; that belongs to [knowledge topology](knowledge-topology.md) and to the per-artifact references.

## Contents

- [Mode resolution](#mode-resolution)
- [Buckets](#buckets)
- [Help mode](#help-mode)
- [Layout declaration and drift](#layout-declaration-and-drift)
- [Significant components](#significant-components)
- [Write allowlist](#write-allowlist)
- [Unchanged predicate](#unchanged-predicate)
- [Preflight plan](#preflight-plan)
- [Waves](#waves)
- [Enforcement gap](#enforcement-gap)
- [Completion report](#completion-report)

## Mode resolution

Resolve one provisional mode from the request signals before reading evidence, then run the layout check. State the final mode and the signal that selected it in the plan.

| Mode | Selecting signal | Write allowlist |
| --- | --- | --- |
| `help` | The request opens with `help`, or asks what this skill can do, which mode applies, or how to phrase the real request. | None. Read-only. |
| `targeted` | The user names explicit paths, directories, or a single document. | Only those normalized destinations. |
| `sync` | No explicit targets, and the repository already realizes its declared knowledge layout. | The approved plan intersected with the requested bucket: existing documents plus missing documents on the closed derived-gap list. |
| `setup` | No explicit targets, and the declared layout is absent, incomplete, or contradicted by what exists on disk. | The approved plan intersected with the requested bucket: the layout and component documents the bucket admits. |

Apply the signals in order and stop at the first match. When two modes remain defensible after the check, do not guess: state both readings and ask which one applies.

`sync` aligns documents to repository evidence and is not a sync contract over managed copies. When the request is about managed-copy state, blockers, or apply flows, stop and ask which run applies before resolving a mode.

The layout check runs in `sync` and in a provisional `setup`, never in `help` or `targeted`. Derive the evidenced domain set, compare it with the declared layout, and escalate `sync` to `setup` when the two disagree. The escalation inherits the requested bucket: a bucketed `sync` escalates to the same bucket in `setup`, and a bucketed run never starts a layout migration. The check only escalates: it never returns `setup` to `sync`, and it never widens `targeted`.

`targeted` never widens into `sync`. A request naming three directories stays at three directories even when the repository clearly needs more; report the wider gap instead of acting on it.

## Help mode

`help` answers a question about this skill and writes nothing. It produces no drafts, no destinations, and no state-changing commands.

Read only what is cheap and decisive: the layout declaration, which root knowledge documents exist, and whether the request already names a path.

Answer in four short parts:

1. **Understood intent** — one sentence restating the request in this skill's vocabulary.
2. **Mode that applies** — the mode the request would resolve to and the signal that selects it.
3. **What would happen** — the destinations at stake, the gate that applies, and what the invocation would leave untouched.
4. **Prompt to run** — one copyable sentence the user can send to start the real invocation.

When the request supports more than one reading, present at most three candidates, each with its mode and its prompt, and ask which one applies. Never pick one silently.

When `help` arrives with no request, summarize the modes, state the repository's current layout and any drift, and name the single most valuable next invocation.

Never start the work the answer describes. `help` ends with the proposed prompt; sending it is the user's decision.

## Layout declaration and drift

A declaration states intent; the repository states fact. Read the declaration, and never accept it as proof that the layout is correct.

Read the declaration from these sources, in precedence order:

1. An explicit instruction in the current request.
2. An accepted ADR recording the domain set.
3. A repository agent-facing documentation guide, such as `docs/agents/domain.md`, when present.
4. The root knowledge documents that actually exist on disk.
5. Nothing declared: the plan proposes a layout with its evidence and asks for approval.

A declaration carries weight only for the artifacts it names and that exist. A statement asserting a layout without naming a single verifiable path is a hint, not a declaration: record it as evidence of intent and derive the layout from the repository.

Compare the declaration against reality and classify the result:

- `realized`: every artifact the declaration names exists, no competing root document exists, and the evidenced domain set matches the declared one.
- `unrealized`: the declaration names an artifact that does not exist.
- `contradicted`: the artifacts on disk implement a different layout than the one declared.
- `understated`: the declared layout is realized, but the evidence supports a richer one, such as a single context declared where two or more domains are evidenced.

All three drift states select `setup`. Report the drift explicitly; a declaration pointing at an absent document is a defect, not a detail. `setup` runs whenever the layout check detects drift, not only on first use: the name describes the work, not the schedule.

In `setup` the declared layout is never inherited. Derive the domain set from evidence, present the declaration as a proposal to confirm, and carry both readings in the plan when they differ.

Changing a declaration is a documentation change like any other. It enters the plan, appears in the allowlist, and is written only after approval. Never update a declaration silently, and never leave a declaration pointing at a document the plan does not create.

A repeated `understated` finding is a decision waiting to be recorded, not a report to reissue. When the user keeps the narrower layout, propose an ADR that records the domain set with its evidence; that record then answers the question for every later invocation.

## Buckets

A request may name a bucket: `only the READMEs` or `only the docs`. The bucket filters the derived document set in `sync` and `setup`; it never replaces the layout check, the plan gate, or the waves.

The readme bucket is classified by file name: every `README.md` anywhere in the repository belongs to it. The docs bucket holds everything under `docs/` plus the root `CONTEXT.md` or `CONTEXT-MAP.md`, except README files.

Bucket membership never overrides the always-excluded paths, the ownership evidence, or the two entry points rule: each excluded member lands in the exclusion ledger with its reason, exactly like any other excluded target.

The derived gaps `sync` fills inside a bucket are a closed list: a component README, `RULES.md`, `docs/adr/README.md`, and the root `README.md`. Every other missing artifact, including `docs/architecture.md` and the layout root document, is shape and escalates.

When the mechanical classification contradicts a plausible reading of the request, the plan declares the mismatch before approval instead of guessing: an intent that says "the documentation" while the bucket excludes `docs/README.md` is a plan note, not a silent exclusion.

## Significant components

A directory is a significant component when it is tracked by version control **and** at least one of the following is evidenced:

- it owns a manifest or entry point, such as an action definition, an infrastructure root with its own state backend, a package manifest, a container definition, a build file, or a command entry point;
- another component, workflow, or document refers to it as a single unit;
- it owns a distinct state, lifecycle, or execution boundary;
- it is a data, configuration, or policy source of truth consumed elsewhere.

Always excluded, without further analysis: paths ignored by version control; vendored, cached, or generated trees; directories that only contain other directories; directories holding a single file already documented by their parent; and test fixtures.

Discovery proposes; it never authorizes. Every discovered directory, and every row of the evidence table in [knowledge topology](knowledge-topology.md), is either a planned target or an entry in the exclusion ledger with a one-line reason. Silent omission is a defect.

## Write allowlist

- In `targeted`, the allowlist is the normalized set of user-supplied destinations.
- In `sync` and `setup`, the allowlist is exactly the approved plan intersected with the requested bucket. Approval is what authorizes a write, not discovery.
- A row outside the requested bucket is reported as excluded with the reason `outside the requested bucket`; it never produces an unplanned write.
- The allowlist never grows after approval. New evidence found while drafting produces a reported gap and, if material, a stop; it never produces an unplanned write.
- Repository governance and contribution files are evidence, never targets. Read them, cite them, place them in the reading order, and leave them untouched.
- A path is generated or externally synchronized only when its own generator or manifest lists that path. A directory pattern is not evidence of ownership: read the entries, because a manifest covering a tree normally enumerates exact paths, and excluding a repository-owned document as managed drops it from the plan without anyone noticing.
- The layout root document is the single exception in `targeted`: the skill may add or update the row describing an authored target, and nothing else in that file. When no root document exists, `targeted` does not create one; it reports the absence.

## Unchanged predicate

Before rewriting an existing document, evaluate this predicate. It is mechanical, so two runs on identical inputs reach the same verdict.

A target is `unchanged` when all of the following hold:

1. Every section its contract requires is present, in the required order.
2. No placeholder, unresolved marker, or empty required section remains.
3. Every relative link resolves from the document's directory.
4. Every generated block is intact and internally consistent.
5. No material claim in the document contradicts current repository evidence.

When the predicate holds, report the target as `unchanged` and do not write it. When it fails, name the failing clause in the plan; that clause is the justification for the rewrite. Stylistic preference is never a justification.

## Preflight plan

`sync` and `setup` must present a plan and obtain approval before the first write. `targeted` does not use this gate.

The plan states, briefly:

- the resolved mode, its selecting signal, and the result of the layout check;
- the layout, its declaration source, the evidenced domain set, and any drift;
- whether the external context-format skill is available, whenever the plan includes a context document;
- one row per planned target with its path, its state under the unchanged predicate, and the reason it is included;
- the exclusion ledger;
- artifacts to be created that do not exist yet;
- the requested bucket, the intent-to-bucket reading, and any mismatch the classification produces;
- out-of-bucket shape drift as a named follow-up block with a copyable `setup` prompt, when the drift is outside the bucket;
- the current wave and what remains for later waves;
- one Mermaid diagram of the resulting topology.

The plan is negotiable line by line. Removing a row moves it to the exclusion ledger with the reason recorded as a user decision. Rejecting the plan means zero writes.

## Waves

Order the plan by reader value: the layout root document first, then the components a reader must understand to use the repository, then the remainder.

Write at most one wave per invocation, and at most ten authored documents in a wave. The ceiling is not a target: when the evidence supports more documents than the wave carries, the plan names what limits it, whether coherence, the ceiling itself, or a user decision. A wave must leave the repository coherent on its own: never publish a document whose links point at artifacts a later wave would create. Report the remaining waves so the next invocation resumes without rediscovery.

A wave partitions documents, never the obligations of an authoring reference. Every rule that reference states for a document, including its sections, its links, and its diagram disposition, is satisfied when that document is written. Treating one obligation as its own later wave leaves every document already published incomplete, and the defect survives review because each wave looked finished on its own.

## Enforcement gap

The skill authors documents and never installs the checks that keep them true. Because that boundary is real, the completion report must name what the repository would need to preserve the result: which properties are worth checking, which existing owner would host the check, and what breaks first without it.

This block is a report, not a change. Never create or modify workflows, actions, validators, coverage manifests, or repository policy files.

## Completion report

Report every target exactly once as `created`, `refreshed`, `unchanged`, `excluded`, or `failed`. Include the evidence used, the validators run and their scope, the exclusion ledger, the enforcement gap, unresolved conflicts, and the next wave.

When a bucket excludes material gaps, such as a missing `RULES.md` for an evidenced domain, elevate them above the ledger boilerplate: name each one with its evidence and the follow-up that would author it.

State what each validator actually covered as counts, not as a verdict. A check that resolved nothing also reports no failures, so a bare pass is compatible with having checked nothing; the counts are what separate the two.

A local validator proves only the paths it actually covered. Do not present it as proof of the whole plan.
