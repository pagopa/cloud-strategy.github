# Workflow Maps

Use this reference when preserving or validating user-visible operational flows.

## Direct Task / Quick Edit

```text
+-----------------------------+
| Clear edit or deterministic  |
| local task                   |
+-----------------------------+
               |
               v
+-----------------------------+
| execute mode                 |
| - applies the change         |
| - runs concrete checks       |
+-----------------------------+
               |
               v
+-----------------------------+
| Outcome with validation      |
| and residual risk            |
+-----------------------------+
```

### Catalog Fast Path

Small catalog maintenance before escalating to retained planning or review.

- Triage `internal-gateway-simple-task` vs `execute` vs `plan` before loading optional references or review lenses.
- First read budget: one owner file, one nearby validator or test, one extra reference only when it changes the next safe action.
- If the target is a repository-owned bundle owner such as `SKILL.md`, inspect the owning bundle root plus relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` before closing coverage or intentional non-action.
- Use a short loop: targeted `rg` or nearby read, patch, nearby test, `make catalog-fast-check`, then `make github-catalog-validation` once at the end.
- Add `CATALOG_FAST_INCLUDE_TOKEN_RISKS=1` only when the change touches always-on guidance or shared contracts.

## End-to-End Delivery / Full Cycle

```text
+--------------------------------+
| Non-trivial repository-owned    |
| work or full-cycle request      |
+--------------------------------+
               |
               v
+-------------------------------+
| define state                   |
| - minimum evidence pass, then  |
|   grill-me Gate 0              |
| - Definition Brief             |
| - Pre-Plan Critical Pass       |
+-------------------------------+
               |
               v
+-------------------------------+
| plan phase                     |
| - retained plan when justified |
| - Decision Brief               |
+-------------------------------+
               |
               v
+-------------------------------+
| checkpoint before execute or   |
| apply-plan unless preapproved  |
+-------------------------------+
               |
               v
+-------------------------------+
| execute or apply-plan          |
| - local delivery or done-*     |
|   retained-plan loop           |
+-------------------------------+
               |
               v
+-------------------------------+
| review evidence or final       |
| outcome with residual risk     |
+-------------------------------+
```

For Gate 0 status, closure, blocking, and realignment, see [`gate-0-protocol.md`](gate-0-protocol.md). At map level: run the minimum evidence pass before Gate 0, and keep downstream plan, review, and retained-plan application blocked until the user closes the active `grill-me` loop.
Do not restate the non-waiver or phase-transition details in maps.

## Idea, Brainstorming & Exploration / Define & Scope

```text
+--------------------------------+
| Intent, success, constraints,   |
| anti-scope, or options unclear  |
+--------------------------------+
               |
               v
+-------------------------------+
| define state                   |
| - smallest evidence pass       |
| - grill-me Gate 0              |
| - Definition Brief             |
| - Pre-Plan Critical Pass       |
+-------------------------------+
               |
               v
+-------------------------------+
| plan, review, critical, or     |
| stop after define-first        |
+-------------------------------+
```

When substantive idea work appears, stop and recommend `internal-gateway-idea-brainstorming` visibly. Operational `define` keeps only clarification needed for the staged workflow.

## Strategy & Decision Framing / Plan & Design

```text
+--------------------------------+
| Ambiguity, governance, rollout, |
| or repository-owned authoring   |
+--------------------------------+
               |
               v
+-------------------------------+
| define state if needed         |
| - Gate 0 and Definition Brief  |
| - Pre-Plan Critical Pass       |
+-------------------------------+
               |
               v
+-------------------------------+
| plan mode                      |
| - requires pre-plan critical:  |
|   confident                    |
| - decision frame and tradeoffs |
+-------------------------------+
               |
               v
+-------------------------------+
| Next-step package              |
+-------------------------------+
               |
               v
+-------------------------------+
| execute, apply-plan, review,   |
| or critical only after         |
| visible checkpoint             |
+-------------------------------+
```

## Review & Quality Gate / Audit & Validate

```text
+-----------------------------+
| Concrete change or artifact  |
+-----------------------------+
               |
               v
+-----------------------------+
| review mode                  |
| - findings first             |
| - severity and confidence    |
| - fix routing plan           |
+-----------------------------+
               |
               v
+-----------------------------+
| Review Gate                  |
| - grill-me satisfied         |
| - critical-master confident  |
+-----------------------------+
               |
               v
+-----------------------------+
| Route each actionable item   |
| to execute, plan, critical,  |
| or defer                     |
+-----------------------------+
```

## Apply/Execute Plan / Apply Retained Plan

```text
+-------------------------------+
| User invokes skill with        |
| approved tmp/ folder           |
+-------------------------------+
               |
               v
+-------------------------------+
| apply-plan entrypoint          |
| - load internal-executing-plans|
| - ignore questions.md         |
| - visible define pre-start     |
|   Gate 0 before execution      |
+-------------------------------+
               |
               v
+-------------------------------+
| done-* loop                    |
| - move completed items         |
| - preserve ledger coverage     |
| - continue across plan files   |
+-------------------------------+
               |
               v
+-------------------------------+
| Check 1 plan coverage          |
| Check 2 contract coverage      |
| Check 3 evidence coverage      |
+-------------------------------+
               |
               v
+-------------------------------+
| If not SHIPPED                 |
| - keep live folder + ledger   |
| - report State + Continuation |
| - emit next-step package      |
+-------------------------------+
               |
               v
+-------------------------------+
| Check 4 close packaging        |
| (SHIPPED only)                 |
| - evidence envelope + report   |
| - matching done-* markers      |
| - remove all numbered files    |
| - preserve and close ledger    |
+-------------------------------+
```

`apply-plan` cannot report `SHIPPED` before Check 4 verifies the physical close package. Non-`SHIPPED` states keep the retained plan live and must say whether execution is `continuing` or `waiting`.

## Runtime Projection

| Runtime surface | Projection |
| --- | --- |
| IDE with agent UI | Users select wrapper agents and approve `handoffs: send=false` buttons. |
| Web or chat-only | Text next-step packages; no agent UI. |
| CLI or plugin runtime with skill loading | Load relevant skills directly. |

## Runtime Context Assembly

For runtimes without native skill loading:

1. Read `AGENTS.md` for repository-wide policy.
2. Read `.github/copilot-instructions.md` as the Copilot-native projection.
3. Select the smallest relevant skill from the prompt, target path, or validation signal, then read that `SKILL.md`.
4. Load only support skills that can change the current phase.
5. Use fresh tool or validator output before any completion claim.
