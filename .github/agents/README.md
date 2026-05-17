# Agents Catalog

This folder contains Copilot wrapper agents for repository-owned operations plus repo-only sync workflows. The portable operational semantics live in skills; these agents provide VS Code route selection, tool scope, and manual handoff UX.

## Skill-First Core

- `internal-gateway-operational-flow` owns the reusable skill-first staged workflow for `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit phases.
- `internal-gateway-critical-master` owns the reusable critical challenge workflow and outcome routing.
- The four internal operational agents are current Copilot wrapper entrypoints, not a separate semantic source.
- Runtime surfaces without Copilot agent UI should read the relevant `SKILL.md` files and use text next-step packages.

## Resolution order

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply the explicit user request and selected skill mode or wrapper behavior.
3. Apply matching `instructions/*.instructions.md` by path.
4. Apply referenced skill details.

## ASCII Workflow Map

These maps describe the expected human-visible flow between direct-entry modes
and Copilot wrappers. They are not hidden dispatch rules. A box is an owner, an
arrow is a transition that should remain visible to the user, and
`handoffs: send=false` means VS Code may offer a button but the user still
reviews and approves the next message.

### 1. Quick execution

Quick execution:

```text
+-----------------------------+
| User asks for a clear edit  |
| or deterministic local task |
+-----------------------------+
              |
              v
+----------------------------+
| internal-delivery-operator |
| - applies the change       |
| - keeps scope local        |
| - runs concrete checks     |
+----------------------------+
              |
              v
+-----------------------------+
| Validation evidence         |
| - command output            |
| - file diff sanity check    |
| - residual risk if any      |
+-----------------------------+
              |
              v
+-----------------------------+
| Final outcome               |
| - files changed             |
| - tests run                 |
| - remaining caveats         |
+-----------------------------+
```

Use this path when the target state is already known. The delivery agent should
not reopen strategy, invent new ownership, or create retained plan files unless
the task unexpectedly becomes non-trivial.

Portable core: `execute` phase in `internal-gateway-operational-flow`.

Good examples:

- "Fix the typo in the internal Python instruction."
- "Add the missing validation command to this existing skill."
- "Rename this one catalog reference and run the focused tests."

Bad fit examples:

- "Redesign how planning and review should cooperate."
- "Decide whether this imported skill should be wrapped or retired."
- "Audit whether the current agent model is still coherent."

#### Delivery use cases

Use `internal-delivery-operator` when the request already contains enough
direction to edit or run commands without first resolving ownership. Delivery is
the right lane for concrete work, not for deciding what the work should mean.
Use `execute` mode directly when the runtime does not expose Copilot wrapper
agents.

```text
+------------------------------+
| Is the desired end state      |
| already clear?                |
+------------------------------+
          | yes                         | no
          v                             v
+-----------------------------+   +--------------------------+
| Is the validation path       |   | internal-planning-leader |
| concrete enough to run?      |   | owns route and design    |
+-----------------------------+   +--------------------------+
          | yes                         ^
          v                             |
+----------------------------+          |
| internal-delivery-operator |          |
| owns the local execution   |          |
+----------------------------+          |
          |                             |
          v                             |
+-----------------------------+         |
| If ambiguity appears, stop  |---------+
| and recommend a lane change |
+-----------------------------+
```

Good delivery requests usually name one of these surfaces:

| Surface | Delivery can own this | Expected validation |
| --- | --- | --- |
| Documentation | Add a requested README section, fix stale wording, update examples after a known behavior change. | Markdown sanity check, focused contract test when docs describe behavior. |
| Agent contract | Apply a known handoff label, tighten an output expectation, remove a stale reference. | Parse frontmatter, run agent contract tests, check catalog validation. |
| Skill metadata | Add a missing `agents/openai.yaml`, fix a frontmatter typo, align a validation paragraph with an existing rule. | Run skill lint and focused catalog tests. |
| Prompt or instruction | Rename a prompt reference, update a scoped instruction after the target behavior is already chosen. | Run inventory or consistency checks plus focused tests. |
| Script or test | Fix a failing assertion, add a regression test for a discovered local gap, adjust a deterministic wrapper. | Run the failing test first when practical, then the focused suite. |
| Mechanical catalog alignment | Replace a stale name across adjacent files after the canonical name is already decided. | Run `rg` for stale names, inventory build, and catalog validation. |

Delivery should produce an answer shaped around evidence:

```text
+------------------------+
| Execution scope        |
+------------------------+
            |
            v
+------------------------+
| Files changed          |
+------------------------+
            |
            v
+------------------------+
| Validation commands    |
+------------------------+
            |
            v
+------------------------+
| Residual risk or none  |
+------------------------+
```

Concrete delivery examples:

- "Add more delivery examples to `.github/agents/README.md` and update the
  README contract test." This is delivery-owned because the requested artifact,
  target file, and validation are clear.
- "The test says the README no longer documents `handoffs: send=false`; restore
  that sentence and run `tests/test_canonical_agents_contract.py`." This is a
  narrow regression fix with a known validation command.
- "Rename `internal-agent-boundary-recommendation-engine` to
  `internal-agent-support-lane-change-engine` everywhere active after planning approved
  the new name." This is delivery-owned only after the naming decision is
  settled.
- "Apply the review finding that says the handoff target must be checked against
  existing canonical agents." This is delivery-owned because review already
  supplied a local fix route.
- "Regenerate `.github/INVENTORY.md` after adding a prompt and run catalog
  validation." This is delivery-owned when the prompt itself is already approved.

Examples that should leave delivery:

- The user asks "which agent should own this new workflow?" That is planning.
- The task reveals a governance rule conflict between `AGENTS.md` and
  `.github/copilot-instructions.md`. That is planning before delivery.
- The main request becomes "prove this design is safe." That is review or
  critical challenge depending on whether the object is a concrete change or a
  reasoning proposal.
- The next action would expand managed external sync scope. That belongs to the
  sync or planning lane, not routine delivery.

Delivery can still cross multiple adjacent files when the change is mechanical
and already decided. The boundary is not file count; the boundary is whether the
agent is executing a known target state with concrete validation.

### 2. Planned work

Planned work turns ambiguity into an execution-ready next-step package. Planning
does not silently become delivery after it writes the plan.

```text
+--------------------------------+
| User brings ambiguity,         |
| governance, or cross-boundary  |
| repository-owned authoring     |
+--------------------------------+
               |
               v
+-------------------------------+
| internal-planning-leader      |
| - frames the decision         |
| - names assumptions           |
| - compares tradeoffs          |
| - selects the next owner      |
+-------------------------------+
               |
               v
+-------------------------------+
| Next-step package             |
| Owner: exact next owner       |
| Scope: files or decisions     |
| Action: one concrete action   |
| Validation: evidence path     |
| Risk: why approval stays      |
|       manual                  |
+-------------------------------+
               |
               | Next step: Implement plan
               | handoffs: send=false
               v
+-------------------------------+
| internal-delivery-operator    |
| - implements the selected     |
|   plan only                   |
| - preserves the validation    |
|   path                        |
+-------------------------------+
```

Use this path when the work needs a decision record, plan, or route selection
before editing. The planning output should be compact enough for delivery to act
without rediscovering the whole problem.

Portable core: `plan` phase or `plan-only` entry point in `internal-gateway-operational-flow`.

Example:

- Request: "The workflow between planning, delivery, review, and critical feels
  inconsistent. Decide the operating model and prepare the first tranche."
- Planning result: direct-entry model remains; add next-step packaging and manual
  handoffs; do not create a coordinator yet.
- Next owner: `internal-delivery-operator`, because the chosen changes are now
  concrete and testable.

#### Planning use cases

Use `internal-planning-leader` when the next correct action is not yet obvious.
Planning is not a slower version of delivery; it exists to settle ownership,
scope, tradeoffs, rollout shape, and validation before files change.
Use `plan` mode directly when the runtime does not expose Copilot wrapper agents.

```text
+--------------------------------+
| Does the request need a choice  |
| before implementation starts?   |
+--------------------------------+
              | yes                         | no
              v                             v
+--------------------------+        +----------------------------+
| internal-planning-leader |        | internal-delivery-operator |
| owns the decision frame  |        | can execute directly       |
+--------------------------+        +----------------------------+
              |
              v
+-------------------------------+
| Produce a selected direction  |
| plus next-step package        |
+-------------------------------+
              |
              v
+-------------------------------+
| Stop before implementation    |
| unless user explicitly asks   |
| planning to continue locally  |
+-------------------------------+
```

Good planning requests usually involve one of these questions:

| Question type | Planning can own this | Expected output |
| --- | --- | --- |
| Ownership | Should this be an agent, skill, instruction, prompt, script, or README change? | Chosen owner, rejected alternatives, next-step package. |
| Scope | Which files and catalog surfaces should move together? | Explicit in-scope and out-of-scope list. |
| Governance | Does the change affect `AGENTS.md`, Copilot projection, inventory, or sync behavior? | Canonical owner decision and projection impact. |
| Sequencing | Should the work happen as one delivery pass or staged phases? | Ordered plan, validation gates, rollback notes. |
| Ambiguity | The user goal is clear but the implementation path is not. | Assumptions, tradeoffs, selected direction. |
| Retained plan | Work spans macro-categories, turns, handoff, or durable decisions. | Numbered files under `tmp/superpowers/<task>/`. |

Concrete planning examples:

- "Decide whether next-step behavior belongs in each agent body or in a shared
  skill." Planning owns the placement decision before delivery edits files.
- "We need a workflow for plan -> delivery -> review -> fixes; design the first
  tranche without creating hidden routers." Planning owns the operating model.
- "This catalog cleanup touches agents, skills, prompts, inventory, and tests;
  decide the safe order." Planning owns sequencing and validation gates.
- "I want to sync this baseline into consumer repos, but I am unsure what should
  remain local." Planning can frame the decision, then route to the sync owner.
- "Create a retained execution plan because this crosses documentation, tests,
  and governance policy." Planning owns the plan artifact.

Examples that should leave planning:

- The target state is now fixed and only local edits remain. Move to delivery.
- The main need is defect-first confidence in an existing change. Move to review.
- The plan is plausible but rests on weak assumptions. Move to critical.
- The work is source-side external resource refresh after scope is approved. Move
  to `local-sync-external-resources`.

Planning should finish with a next-step package:

```text
+-------------------------------+
| Owner: exact next owner       |
| Scope: files or decision area |
| Action: one concrete action   |
| Validation: expected evidence |
| Risk: why approval is manual  |
+-------------------------------+
```

### 3. Audited work

Audited work is for defect-first review after a change exists or when correctness
evidence is the main request. Review owns findings and fix routing, not fixes.

```text
+-----------------------------+
| A change exists or the user |
| asks for merge readiness    |
+-----------------------------+
              |
              v
+----------------------------+
| internal-delivery-operator |
| - reports changed files    |
| - reports validation       |
| - exposes residual risk    |
+----------------------------+
              |
              | Next step: Review result
              | handoffs: send=false
              v
+-----------------------------+
| internal-review-guard       |
| - findings first            |
| - severity and confidence   |
| - causal layer              |
| - fix routing plan          |
+-----------------------------+
              |
              +------------------------------+
              |                              |
              | Next action: Apply local     |
              | fixes                        |
              | handoffs: send=false         |
              v                              |
+----------------------------+               |
| internal-delivery-operator |               |
| - applies narrow fixes     |               |
| - runs stated validation   |               |
+----------------------------+               |
                                             |
              +------------------------------+
              |
              | Next action: Re-plan larger changes
              | or pressure-test unresolved decision
              | handoffs: send=false
              v
+--------------------------------+
| internal-planning-leader       |
| or internal-critical-master    |
+--------------------------------+
```

Use this path when the user asks "is this right?", "what is risky?", or "review
this before I trust it." A good review answer should make missing validation a
finding, not a footnote.

Portable core: `review` entry point in `internal-gateway-operational-flow`, with
`internal-code-review` as the tactical review engine.

Example:

- Request: "Check whether the new agent handoffs really work as expected."
- Review result: parse each agent frontmatter, assert each handoff target exists,
  assert every handoff keeps `send: false`, and verify the README documents the
  manual transition model.
- Next action: delivery applies small fixes if the finding is local; planning
  owns larger workflow redesign.

#### Review use cases

Use `internal-review-guard` when the main question is "what is wrong, risky, or
insufficiently validated?" Review is evidence-first and defect-first. It does
not implement the fix, even when the fix is obvious.
Use `review` mode directly when the runtime does not expose Copilot wrapper
agents.

```text
+-------------------------------+
| Does a concrete artifact or    |
| change already exist?          |
+-------------------------------+
              | yes                         | no
              v                             v
+-----------------------------+     +--------------------------+
| Is correctness evidence      |     | internal-planning-leader |
| the main need?               |     | owns design first        |
+-----------------------------+     +--------------------------+
              | yes
              v
+-----------------------+
| internal-review-guard |
| owns findings, risk,  |
| and fix routing       |
+-----------------------+
              |
              v
+------------------------------+
| Route each actionable finding |
| to delivery, planning,        |
| critical, or defer            |
+------------------------------+
```

Good review requests usually name one of these review surfaces:

| Surface | Review can own this | Evidence to inspect |
| --- | --- | --- |
| Changed files | Find defects, regressions, stale references, or missing updates. | Diff, adjacent contracts, tests. |
| Agent behavior | Validate routing boundaries, handoff targets, tool contracts, and output expectations. | Agent frontmatter, body sections, contract tests. |
| Skill behavior | Check if a skill is hollow, overloaded, stale, or mis-scoped. | `SKILL.md`, references, `agents/openai.yaml`, skill lint. |
| Documentation claims | Verify whether README examples match live files and tests. | Target docs, catalog files, executable checks. |
| Validation evidence | Decide whether the run commands actually prove the claim. | Test output, skipped checks, residual risk. |
| Merge readiness | Identify blockers before handoff or PR. | Full validation wrapper, changed-file review, open gaps. |

Review findings should use this structure:

```text
+------------------------------+
| Finding                       |
| - severity                    |
| - confidence                  |
| - evidence                    |
+------------------------------+
              |
              v
+------------------------------+
| Causal layer                  |
| - why this happened           |
| - what assumption failed      |
+------------------------------+
              |
              v
+------------------------------+
| Fix routing plan              |
| - delivery                    |
| - planning                    |
| - critical                    |
| - defer with residual risk    |
+------------------------------+
```

Concrete review examples:

- "Review whether the delivery examples in the README are enough to guide future
  users." Review owns evidence and missing-case findings.
- "Check that every `handoffs:` target in the four canonical agents points to a
  real canonical agent and keeps `send: false`." Review owns contract validation.
- "Look at this catalog change and tell me whether inventory, tests, and docs are
  aligned." Review owns cross-surface defect detection.
- "The validation passed, but tell me what it did not prove." Review owns
  evidence gaps and residual risk.
- "Find any stale references after this rename." Review owns stale-name detection
  and routes fixes back to delivery.

Examples that should leave review:

- The user asks to apply the fix. Move to delivery.
- The finding requires deciding a new operating model. Move to planning.
- The concern is a weak assumption in a proposed design, not a concrete defect.
  Move to critical.
- The user wants a broad source catalog refresh. Move to sync or planning first.

### 4. Challenged decisions

Challenge is for pressure-testing reasoning before action. It is deliberately
not a routine review lane and should not implement the solution it critiques.

```text
+--------------------------------+
| A proposal, plan, or decision  |
| has assumptions worth testing  |
+--------------------------------+
               |
               v
+-------------------------------+
| internal-planning-leader      |
| - writes or selects the plan  |
| - identifies the decision     |
|   surface                     |
+-------------------------------+
               |
               | Next step: Pressure-test plan
               | handoffs: send=false
               v
+-------------------------------+
| internal-critical-master      |
| - strongest objection first   |
| - hidden assumptions          |
| - failure modes               |
| - alternative framing         |
| - closing synthesis           |
+-------------------------------+
               |
               | Next step: Reformulate plan,
               | implement clear next step,
               | or review evidence
               | handoffs: send=false
               v
+-------------------------------+
| internal-planning-leader,     |
| internal-delivery-operator,   |
| or internal-review-guard      |
| - acts only on the explicit   |
|   critical outcome            |
+-------------------------------+
```

Use this path for non-banal decisions where the cost of acting on weak reasoning
is higher than the cost of one pressure-test pass.

Portable core: `internal-gateway-critical-master`.

Example:

- Request: "Before we create a coordinator agent, pressure-test whether that
  would actually reduce friction."
- Critical result: strongest objection is hidden routing complexity; direct
  entry plus manual next-step packages may solve the current pain with less
  governance risk.
- Outcome: `reformulate-plan`, because the plan must be reformulated before
  delivery touches files.
- Next owner: `internal-planning-leader`.

#### Critical challenge use cases

Use `internal-critical-master` when the risky part is reasoning quality, not an
already-observed defect. Critical challenge should expose hidden assumptions,
failure modes, overfitting, and missed alternatives before implementation starts.
Use `internal-gateway-critical-master` directly when the runtime does not expose
Copilot wrapper agents. Use `internal-critical-master` when VS Code wrapper UX
is useful.

```text
+------------------------------+
| Is there a proposal, plan,    |
| or decision to attack?        |
+------------------------------+
            | yes                         | no
            v                             v
+-----------------------------+   +--------------------------+
| Is the main risk weak        |   | internal-planning-leader |
| reasoning or hidden premise? |   | frames the plan first    |
+-----------------------------+   +--------------------------+
            | yes
            v
+--------------------------+
| internal-critical-master |
| owns pressure testing    |
+--------------------------+
            |
            v
+-----------------------------+
| Closing synthesis, then      |
| recommend reformulation,     |
| review, or delivery          |
+-----------------------------+
```

Good challenge requests usually involve one of these pressure points:

| Pressure point | Critical can own this | Expected output |
| --- | --- | --- |
| Hidden assumption | What must be true for this plan to work? | Strongest assumption gap and why it matters. |
| Failure mode | How could this plan fail after appearing correct? | Pre-mortem with likely failure path. |
| Overengineering | Is this solving a smaller problem with too much machinery? | Simpler alternative or scope compression. |
| Underengineering | Is the plan skipping necessary governance, tests, or safety? | Missing constraint and downstream consequence. |
| False tradeoff | Are we choosing between two options when a third framing exists? | Reframed decision surface. |
| Timing risk | What breaks if this is done now versus later? | Sequence challenge and recommended next owner. |

Concrete critical examples:

- "Pressure-test the idea of adding a coordinator agent." Critical challenges
  hidden routing complexity, maintenance cost, and ping-pong risk.
- "Attack this retained plan before delivery implements it." Critical looks for
  assumptions that planning normalized too quickly.
- "Is direct entry actually enough for the workflow, or are we avoiding needed
  orchestration?" Critical tests both downside and upside.
- "What is the strongest reason not to import this upstream skill?" Critical
  focuses on strategic fit, not line-level defects.
- "Find the weakest part of this migration plan." Critical identifies the single
  most important premise to resolve before action.

Examples that should leave critical:

- The user asks for implementation. Move to delivery.
- The user asks for final plan reformulation. Move to planning.
- The user asks whether a concrete diff is correct. Move to review.
- The user asks for open-ended idea generation. Use planning or brainstorming
  support instead.

Critical should end with synthesis, not endless skepticism. The useful output is
the strongest surviving objection, what uncertainty remains, and which owner
should act next.

### 5. Source and consumer sync workflows

The two sync agents are repo-only command centers. They are not substitutes for
the four canonical operational agents.

Source-side catalog governance:

```text
+----------------------------------+
| User asks to refresh, rationalize |
| or retire source catalog assets   |
+----------------------------------+
                |
                v
+---------------------------------+
| local-sync-external-resources   |
| - managed external resources    |
| - overlap decisions             |
| - imported override registry    |
| - source catalog validation     |
+---------------------------------+
                |
                v
+----------------------------------+
| Source repository catalog state  |
| remains aligned with AGENTS.md,  |
| copilot-instructions.md, and     |
| INVENTORY.md                     |
+----------------------------------+
```

Consumer baseline propagation:

```text
+----------------------------------+
| User asks to sync this baseline   |
| into a consumer repository        |
+----------------------------------+
                |
                v
+-----------------------------------------+
| local-sync-global-copilot-configs       |
| into-repo                               |
| - plan by default                       |
| - preserve target local-* assets        |
| - preserve override layer               |
| - apply only on explicit request        |
+-----------------------------------------+
                |
                v
+----------------------------------+
| Consumer repository gets the      |
| managed baseline without losing   |
| local exceptions                  |
+----------------------------------+
```

Use `local-sync-external-resources` when changing this repository's source
catalog. Use `local-sync-global-copilot-configs-into-repo` when pushing the
managed baseline into another repository.

#### Sync use cases

Use sync agents only when the task is about catalog synchronization or baseline
propagation. They are command centers for a specific operational surface, not
general-purpose delivery agents.

```text
+------------------------------+
| Is the source catalog in this |
| repository being changed?     |
+------------------------------+
        | yes                           | no
        v                               v
+-------------------------------+   +--------------------------------+
| local-sync-external-resources |   | Is a consumer repo receiving   |
| owns source-side sync         |   | this baseline?                 |
+-------------------------------+   +--------------------------------+
                                        | yes                    | no
                                        v                        v
                         +--------------------------------+   +--------------------------+
                         | local-sync-global-copilot      |   | Pick planning, delivery, |
                         | configs-into-repo owns target  |   | review, or critical      |
                         | baseline propagation           |   +--------------------------+
                         +--------------------------------+
```

Source-side sync examples:

- "Refresh the managed `mattpocock-*` skills declared in the source-side map."
- "Audit imported `obra-*` assets for overlap with internal owners."
- "Apply approved imported-asset override patches after upstream refresh."
- "Retire a managed external skill after the user explicitly narrows scope."
- "Check that `AGENTS.md`, `.github/copilot-instructions.md`, and inventory stay
  aligned after source catalog changes."

Consumer propagation examples:

- "Plan syncing this repository's Copilot baseline into another repo."
- "Apply the approved baseline sync while preserving target `local-*` assets."
- "Check whether the consumer override layer changes the effective guidance."
- "Bring `LESSONS_LEARNED.md` structure into a target repo without losing local
  lesson rows."
- "Report which managed files would change before applying sync."

Examples that should leave sync:

- A single local README or test edit remains after sync planning. Move to
  delivery.
- The user is still deciding whether a new catalog family should exist. Move to
  planning.
- The user asks for correctness review of the sync result. Move to review.
- The user asks whether the sync strategy itself is flawed. Move to critical.

## Use Examples

- Clear local edit with known validation: start with `execute` mode or `internal-delivery-operator`.
- Catalog redesign, routing change, or retained plan: start with `plan` mode or `internal-planning-leader`.
- "Check whether this is correct before merge": start with `review` mode or `internal-review-guard`.
- "Find the weakest assumption in this plan": start with `internal-gateway-critical-master` or `internal-critical-master`.
- Source-side external catalog sync: start with `local-sync-external-resources`.
- Consumer repository baseline propagation: start with `local-sync-global-copilot-configs-into-repo`.

More concrete examples:

| User request shape | Start with | Why |
| --- | --- | --- |
| "Update one README section and run the related test." | `execute` or `internal-delivery-operator` | Scope and validation are already concrete. |
| "Decide whether this should be an agent, a skill, or an instruction." | `plan` or `internal-planning-leader` | The core work is ownership and placement. |
| "Review these agent changes for routing regressions." | `review` or `internal-review-guard` | The job is defect-first validation, not implementation. |
| "Attack this plan before I apply it." | `internal-gateway-critical-master` or `internal-critical-master` | The job is assumption pressure-testing. |
| "Refresh the managed `obra-*` skills from upstream." | `local-sync-external-resources` | The job is source-side external catalog sync. |
| "Plan the propagation of this baseline into another repo." | `local-sync-global-copilot-configs-into-repo` | The job is consumer baseline alignment. |

If a request starts in the wrong lane, the selected agent should stop, explain
the mismatch, and recommend one better owner through `internal-agent-support-lane-change-engine`.
It should not continue by acting as a hidden router.

## Owner Selection

- `execute` mode or `internal-delivery-operator`: clear local execution, deterministic realignment, concrete validation.
- `plan` mode or `internal-planning-leader`: ambiguity, cross-boundary tradeoffs, non-trivial repository-owned authoring, rollout decisions.
- `review` mode or `internal-review-guard`: defect-first review, merge readiness, regression analysis, validation evidence.
- `internal-gateway-critical-master` or `internal-critical-master`: pre-mortem, assumption pressure test, failure modes, alternative framing.
- `local-sync-external-resources`: source-side `.github/` catalog sync, rationalization, overlap cleanup, managed external resources.
- `local-sync-global-copilot-configs-into-repo`: consumer-repository baseline propagation.

Safe fallback: use `plan` mode or `internal-planning-leader` when two or more owners still plausibly fit.

## When not to use

- Do not use `internal-planning-leader` for banal local edits once the target state is known.
- Do not use `internal-delivery-operator` when routing, ownership, or governance is still being decided.
- Do not use `internal-review-guard` to implement fixes.
- Do not use `internal-critical-master` as a routine code reviewer.
- Do not use sync agents for ordinary local implementation outside their sync scope.

## Next steps

The four Copilot wrapper agents can expose VS Code `handoffs:` buttons for user-visible transitions. The buttons keep `send: false`; the user still approves the move. Responses should also include a compact next-step package because some surfaces may ignore handoff buttons.

Use `Next step:` labels for planned transitions and `Next action:` labels for review remediation.

## Token budget

Pick the narrowest owner that can complete the current phase. The right agent should reduce preamble, avoid re-planning solved work, and keep output focused on the next decision or validation evidence.

## Repo-only agents

- `local-sync-external-resources`
- `local-sync-global-copilot-configs-into-repo`

PR-focused work should use the `internal-github-pr` skill because this repository does not currently ship a dedicated PR agent.
