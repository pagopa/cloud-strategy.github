# Knowledge Scope

Use this reference to decide **what the skill may touch** before any drafting starts. It owns mode resolution, target discovery, the write allowlist, the preflight plan, and the completion report. It never decides document structure; that belongs to [knowledge topology](knowledge-topology.md) and to the per-artifact references.

## Contents

- [Mode resolution](#mode-resolution)
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
| `refresh` | No explicit targets, and the repository already realizes its declared knowledge layout. | The approved plan: existing documents plus missing documents for significant components. |
| `bootstrap` | No explicit targets, and the declared layout is absent, incomplete, or contradicted by what exists on disk. | The approved plan: the layout root document, the derived topology, and component documents. |

Apply the signals in order and stop at the first match. When two modes remain defensible after the check, do not guess: state both readings and ask which one applies.

The layout check runs in `refresh` and in a provisional `bootstrap`, never in `help` or `targeted`. Derive the evidenced domain set, compare it with the declared layout, and escalate `refresh` to `bootstrap` when the two disagree. The check only escalates: it never returns `bootstrap` to `refresh`, and it never widens `targeted`.

`targeted` never widens into `refresh`. A request naming three directories stays at three directories even when the repository clearly needs more; report the wider gap instead of acting on it.

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

All three drift states select `bootstrap`. Report the drift explicitly; a declaration pointing at an absent document is a defect, not a detail.

In `bootstrap` the declared layout is never inherited. Derive the domain set from evidence, present the declaration as a proposal to confirm, and carry both readings in the plan when they differ.

Changing a declaration is a documentation change like any other. It enters the plan, appears in the allowlist, and is written only after approval. Never update a declaration silently, and never leave a declaration pointing at a document the plan does not create.

A repeated `understated` finding is a decision waiting to be recorded, not a report to reissue. When the user keeps the narrower layout, propose an ADR that records the domain set with its evidence; that record then answers the question for every later invocation.

## Significant components

A directory is a significant component when it is tracked by version control **and** at least one of the following is evidenced:

- it owns a manifest or entry point, such as an action definition, an infrastructure root with its own state backend, a package manifest, a container definition, a build file, or a command entry point;
- another component, workflow, or document refers to it as a single unit;
- it owns a distinct state, lifecycle, or execution boundary;
- it is a data, configuration, or policy source of truth consumed elsewhere.

Always excluded, without further analysis: paths ignored by version control; vendored, cached, or generated trees; directories that only contain other directories; directories holding a single file already documented by their parent; and test fixtures.

Discovery proposes; it never authorizes. Every discovered directory is either a planned target or an entry in the exclusion ledger with a one-line reason. Silent omission is a defect.

## Write allowlist

- In `targeted`, the allowlist is the normalized set of user-supplied destinations.
- In `refresh` and `bootstrap`, the allowlist is exactly the approved plan. Approval is what authorizes a write, not discovery.
- The allowlist never grows after approval. New evidence found while drafting produces a reported gap and, if material, a stop; it never produces an unplanned write.
- Repository governance and contribution files are evidence, never targets. Read them, cite them, place them in the reading order, and leave them untouched.
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

`refresh` and `bootstrap` must present a plan and obtain approval before the first write. `targeted` does not use this gate.

The plan states, briefly:

- the resolved mode, its selecting signal, and the result of the layout check;
- the layout, its declaration source, the evidenced domain set, and any drift;
- whether the external context-format skill is available, whenever the plan includes a context document;
- one row per planned target with its path, its state under the unchanged predicate, and the reason it is included;
- the exclusion ledger;
- artifacts to be created that do not exist yet;
- the current wave and what remains for later waves;
- one Mermaid diagram of the resulting topology.

The plan is negotiable line by line. Removing a row moves it to the exclusion ledger with the reason recorded as a user decision. Rejecting the plan means zero writes.

## Waves

Order the plan by reader value: the layout root document first, then the components a reader must understand to use the repository, then the remainder.

Write at most one wave per invocation, and at most ten authored documents in a wave. A wave must leave the repository coherent on its own: never publish a document whose links point at artifacts a later wave would create. Report the remaining waves so the next invocation resumes without rediscovery.

## Enforcement gap

The skill authors documents and never installs the checks that keep them true. Because that boundary is real, the completion report must name what the repository would need to preserve the result: which properties are worth checking, which existing owner would host the check, and what breaks first without it.

This block is a report, not a change. Never create or modify workflows, actions, validators, coverage manifests, or repository policy files.

## Completion report

Report every target exactly once as `created`, `refreshed`, `unchanged`, `excluded`, or `failed`. Include the evidence used, the validators run and their scope, the exclusion ledger, the enforcement gap, unresolved conflicts, and the next wave.

A local validator proves only the paths it actually covered. Do not present it as proof of the whole plan.
