# Agents Catalog

This folder contains custom agents for repository-owned direct-owner operations plus repo-only sync workflows.

## Resolution order

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply the explicit user request and selected agent behavior.
3. Apply matching `instructions/*.instructions.md` by path.
4. Apply referenced skill details.

## ASCII Workflow Map

These maps describe the expected human-visible flow between direct-entry agents.
They are not hidden dispatch rules. A box is an owner, an arrow is a transition
that should remain visible to the user, and `handoffs: send=false` means VS Code
may offer a button but the user still reviews and approves the next message.

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
  `internal-agent-lane-change-engine` everywhere active after planning approved
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

Example:

- Request: "The workflow between planning, delivery, review, and critical feels
  inconsistent. Decide the operating model and prepare the first tranche."
- Planning result: direct-entry model remains; add next-step packaging and manual
  handoffs; do not create a coordinator yet.
- Next owner: `internal-delivery-operator`, because the chosen changes are now
  concrete and testable.

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

Example:

- Request: "Check whether the new agent handoffs really work as expected."
- Review result: parse each agent frontmatter, assert each handoff target exists,
  assert every handoff keeps `send: false`, and verify the README documents the
  manual transition model.
- Next action: delivery applies small fixes if the finding is local; planning
  owns larger workflow redesign.

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
               | Next step: Reformulate plan
               | handoffs: send=false
               v
+-------------------------------+
| internal-planning-leader      |
| - reformulates if needed      |
| - recommends delivery only    |
|   after assumptions settle    |
+-------------------------------+
```

Use this path for non-banal decisions where the cost of acting on weak reasoning
is higher than the cost of one pressure-test pass.

Example:

- Request: "Before we create a coordinator agent, pressure-test whether that
  would actually reduce friction."
- Critical result: strongest objection is hidden routing complexity; direct
  entry plus manual next-step packages may solve the current pain with less
  governance risk.
- Next owner: `internal-planning-leader`, because the plan must be reformulated
  before delivery touches files.

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

## Use Examples

- Clear local edit with known validation: start with `internal-delivery-operator`.
- Catalog redesign, routing change, or retained plan: start with `internal-planning-leader`.
- "Check whether this is correct before merge": start with `internal-review-guard`.
- "Find the weakest assumption in this plan": start with `internal-critical-master`.
- Source-side external catalog sync: start with `local-sync-external-resources`.
- Consumer repository baseline propagation: start with `local-sync-global-copilot-configs-into-repo`.

More concrete examples:

| User request shape | Start with | Why |
| --- | --- | --- |
| "Update one README section and run the related test." | `internal-delivery-operator` | Scope and validation are already concrete. |
| "Decide whether this should be an agent, a skill, or an instruction." | `internal-planning-leader` | The core work is ownership and placement. |
| "Review these agent changes for routing regressions." | `internal-review-guard` | The job is defect-first validation, not implementation. |
| "Attack this plan before I apply it." | `internal-critical-master` | The job is assumption pressure-testing. |
| "Refresh the managed `obra-*` skills from upstream." | `local-sync-external-resources` | The job is source-side external catalog sync. |
| "Plan the propagation of this baseline into another repo." | `local-sync-global-copilot-configs-into-repo` | The job is consumer baseline alignment. |

If a request starts in the wrong lane, the selected agent should stop, explain
the mismatch, and recommend one better owner through `internal-agent-lane-change-engine`.
It should not continue by acting as a hidden router.

## Owner selection

- `internal-delivery-operator`: clear local execution, deterministic realignment, concrete validation.
- `internal-planning-leader`: ambiguity, cross-boundary tradeoffs, non-trivial repository-owned authoring, rollout decisions.
- `internal-review-guard`: defect-first review, merge readiness, regression analysis, validation evidence.
- `internal-critical-master`: pre-mortem, assumption pressure test, failure modes, alternative framing.
- `local-sync-external-resources`: source-side `.github/` catalog sync, rationalization, overlap cleanup, managed external resources.
- `local-sync-global-copilot-configs-into-repo`: consumer-repository baseline propagation.

Safe fallback: use `internal-planning-leader` when two or more owners still plausibly fit.

## When not to use

- Do not use `internal-planning-leader` for banal local edits once the target state is known.
- Do not use `internal-delivery-operator` when routing, ownership, or governance is still being decided.
- Do not use `internal-review-guard` to implement fixes.
- Do not use `internal-critical-master` as a routine code reviewer.
- Do not use sync agents for ordinary local implementation outside their sync scope.

## Next steps

The four canonical agents can expose VS Code `handoffs:` buttons for user-visible transitions. The buttons keep `send: false`; the user still approves the move. Agent responses should also include a compact next-step package because some surfaces may ignore handoff buttons.

Use `Next step:` labels for planned transitions and `Next action:` labels for review remediation.

## Token budget

Pick the narrowest owner that can complete the current phase. The right agent should reduce preamble, avoid re-planning solved work, and keep output focused on the next decision or validation evidence.

## Repo-only agents

- `local-sync-external-resources`
- `local-sync-global-copilot-configs-into-repo`

PR-focused work should use the `internal-pr-editor` skill because this repository does not currently ship a dedicated PR editor agent.
