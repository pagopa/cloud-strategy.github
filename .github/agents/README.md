# Agents Catalog

This folder contains Copilot wrapper agents for repository-owned operations plus
repo-only sync workflows. The portable operational semantics live in skills;
these agents provide VS Code route selection, tool scope, and manual handoff UX.

## Skill-First Core

- `internal-gateway-operational-flow` owns the staged workflow for `full-cycle`,
  `plan-only`, `apply-plan`, `review`, and explicit `plan`, `execute`, or
  `review` phases.
- `internal-gateway-critical-master` owns critical challenge, pre-mortem,
  hidden-assumption testing, failure-mode analysis, and reframing.
- `internal-gateway-simple-task` owns concrete low-to-medium-risk answer, edit,
  diagnose, validate, or escalate tasks that do not need staged workflow.
- Runtime surfaces without Copilot agent UI should read the relevant `SKILL.md`
  files and use text next-step packages.

## Resolution Order

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply the explicit user request and selected gateway skill or wrapper.
3. Apply matching `instructions/*.instructions.md` by path.
4. Apply referenced skill details.

## Active Gateway Wrappers

| Wrapper | Core skill | Use when |
| --- | --- | --- |
| `internal-gateway-operational-flow` | `internal-gateway-operational-flow` | Work needs `plan`, `execute`, `apply-plan`, `review`, `full-cycle`, or a visible next-step package. |
| `internal-gateway-critical-master` | `internal-gateway-critical-master` | A proposal, plan, decision, or assumption set needs pressure before action. |
| `internal-gateway-simple-task` | `internal-gateway-simple-task` | A concrete low-to-medium-risk task can finish through one focused lane. |

## ASCII Workflow Map

These maps describe the expected human-visible flow. They are not hidden
dispatch rules. A box is an owner, an arrow is a transition that should remain
visible to the user, and `handoffs: send=false` means VS Code may offer a button
but the user still reviews and approves the next message.

### 1. Simple Fast Path

```text
+-----------------------------+
| User asks for concrete work |
| with a focused validation   |
+-----------------------------+
              |
              v
+-------------------------------+
| internal-gateway-simple-task  |
| - answer, edit, diagnose,     |
|   validate, or escalate       |
| - stay single-lane            |
+-------------------------------+
              |
              v
+-----------------------------+
| Focused validation evidence |
| and residual risk           |
+-----------------------------+
```

Use this path when the target state is already clear and the work does not need
retained-plan execution, review mode, rollout decisions, or pressure testing.

### 2. Staged Operational Flow

```text
+--------------------------------+
| User brings staged work,        |
| review, apply-plan, or routing  |
+--------------------------------+
               |
               v
+-----------------------------------+
| internal-gateway-operational-flow |
| - selects one visible phase       |
| - keeps next-step packages        |
| - runs completion checks          |
+-----------------------------------+
               |
               v
+--------------------------------+
| Check 1, Check 2, Check 3      |
| or a visible blocker package   |
+--------------------------------+
```

Use this path for `full-cycle`, `plan-only`, `apply-plan`, `review`, or explicit
`plan`, `execute`, and `review` requests. The wrapper is broad because the core
skill owns the phase boundaries.

### 3. Critical Challenge

```text
+--------------------------------+
| A proposal, plan, or decision  |
| has assumptions worth testing  |
+--------------------------------+
               |
               v
+--------------------------------+
| internal-gateway-critical      |
| master                         |
| - strongest objection first    |
| - explicit outcome             |
| - next-step package            |
+--------------------------------+
               |
               v
+-----------------------------------+
| operational flow, simple task,   |
| continued critical, or accepted  |
| risk                             |
+-----------------------------------+
```

Use this path when the risky part is reasoning quality, not an already-observed
defect or a routine implementation step.

### 4. Sync Workflows

The two sync agents are repo-only command centers. They are not substitutes for
gateway wrappers.

```text
+------------------------------+
| Source catalog sync or       |
| consumer baseline sync       |
+------------------------------+
        | source                         | consumer
        v                                v
+-------------------------------+   +--------------------------------+
| local-sync-external-resources |   | local-sync-global-copilot      |
| owns source-side catalog      |   | configs-into-repo owns target  |
| governance                    |   | baseline propagation           |
+-------------------------------+   +--------------------------------+
```

Use `local-sync-external-resources` when changing this repository's source
catalog. Use `local-sync-global-copilot-configs-into-repo` when pushing the
managed baseline into another repository.

## Use Examples

| User request shape | Start with | Why |
| --- | --- | --- |
| "Update one README section and run the related test." | `internal-gateway-simple-task` | Scope and validation are already concrete. |
| "Apply the approved retained plan under `tmp/superpowers/example`." | `internal-gateway-operational-flow` | `apply-plan` needs the retained-plan `done-*` loop. |
| "Decide whether this should be an agent, a skill, or an instruction." | `internal-gateway-operational-flow` | The core work is ownership and placement. |
| "Review these agent changes for routing regressions." | `internal-gateway-operational-flow` | The job is defect-first validation through review mode. |
| "Attack this plan before I apply it." | `internal-gateway-critical-master` | The job is assumption pressure-testing. |
| "Refresh the managed `obra-*` skills from upstream." | `local-sync-external-resources` | The job is source-side external catalog sync. |
| "Plan the propagation of this baseline into another repo." | `local-sync-global-copilot-configs-into-repo` | The job is consumer baseline alignment. |

If a request starts in the wrong lane, the selected agent should stop, explain
the mismatch, and recommend one better owner through
`internal-agent-support-lane-change-engine`. It should not continue by acting as
a hidden router.

## Owner Selection

- `internal-gateway-simple-task`: concrete low-to-medium-risk answer, edit,
  diagnose, validate, or escalate tasks.
- `internal-gateway-operational-flow`: staged planning, execution, retained-plan
  application, review, full-cycle work, and visible next-step packages.
- `internal-gateway-critical-master`: pre-mortem, assumption pressure test,
  failure modes, and alternative framing.
- `local-sync-external-resources`: source-side `.github/` catalog sync,
  rationalization, overlap cleanup, and managed external resources.
- `local-sync-global-copilot-configs-into-repo`: consumer-repository baseline
  propagation.

Safe fallback: use `internal-gateway-operational-flow` when two or more gateway
owners still plausibly fit.

## When Not To Use

- Do not use `internal-gateway-simple-task` for retained-plan execution, review
  mode, or governance-sensitive redesign.
- Do not use `internal-gateway-operational-flow` for a simple single-lane task
  that can finish faster through `internal-gateway-simple-task`.
- Do not use `internal-gateway-critical-master` as a routine code reviewer or
  implementation owner.
- Do not use sync agents for ordinary local implementation outside their sync
  scope.

## Next Steps

The three gateway wrappers can expose VS Code `handoffs:` buttons for
user-visible transitions. The buttons keep `send: false`; the user still
approves the move. Responses should also include a compact next-step package
because some surfaces may ignore handoff buttons.

Use `Next step:` labels for planned transitions and `Next action:` labels for
local remediation or simple-task transitions.

## Token Budget

Pick the narrowest owner that can complete the current phase. The right wrapper
should reduce preamble, avoid re-planning solved work, and keep output focused
on the next decision or validation evidence.

## Repo-Only Agents

- `local-sync-external-resources`
- `local-sync-global-copilot-configs-into-repo`

PR-focused work should use the `internal-github-pr` skill because this
repository does not currently ship a dedicated PR agent.
