---
name: internal-gateway-operational-flow
description: Use when repository-owned work needs a skill-first staged operational workflow, including full-cycle, plan-only, apply-plan, review, or explicit plan, execute, and review phases.
---

# Internal Gateway Operational Flow

Use this skill as the portable skill-first operational core for repository-owned staged work. Copilot agents may wrap it with frontmatter, tools, and `handoffs:`, but the reusable workflow semantics live here so runtimes without agent UI can still follow the same model.

## When to use

- Repository-owned operational work needs a portable staged workflow across `plan`, `execute`, `review`, critical challenge, or retained-plan application.
- The user selects a gateway skill in a runtime such as Codex and needs visible phases instead of manual wrapper-agent switching.
- A runtime such as ChatGPT, Codex plugin, or Codex CLI needs the workflow without Copilot agent UI.
- A Copilot wrapper needs the shared semantic owner for planning, delivery, or review behavior.
- A next-step package must preserve the operational transition across surfaces.

## When not to use

- The primary need is critical challenge or pre-mortem work; use `internal-gateway-critical-master`.
- The work is concrete, low to medium risk, and only needs skill-first quick routing, lightweight analysis, support-skill selection, execution, or focused validation; use `internal-gateway-simple`.
- The work is source-side sync governance or consumer baseline propagation; use the repo-only sync owners.
- The user only needs a narrow runtime or domain skill after the operational mode is already settled.

## Skill-First Staged Entry Points

Select one workflow entry point from the user prompt, then run one active phase at a time inside that workflow.

| Entrypoint | Use when | First active phase |
| --- | --- | --- |
| `full-cycle` | The user asks for end-to-end non-trivial work or explicitly wants plan, challenge, apply, and review. | `plan` |
| `plan-only` | The user asks for a plan, decision brief, or retained plan without implementation. | `plan` |
| `apply-plan` | The user asks to apply an approved retained plan under `tmp/superpowers/`. | `execute` with `internal-executing-plans` |
| `review` | The user asks for defect-first review, merge readiness, or evidence analysis. | `review` |
| `mode-explicit` | The user directly asks for `plan`, `execute`, or `review`. | The named phase |

Do not create new gateway skills for `plan`, `apply`, or `review`. Use this skill to expose the staged workflow and delegate deep procedure to the owning support skills.

## Core Contract

- Choose one active phase at a time inside the selected workflow.
- Each active phase declares phase, logical owner, scope, anti-scope, action, validation, risk, and the next checkpoint or decision.
- If the entry point or phase is unclear, use `plan` as the safe fallback instead of dispatching automatically.
- Keep direct entry and manual transitions visible to the user.
- Use `internal-agent-support-lane-change-engine` when the selected mode no longer fits.
- Use `internal-agent-support-next-step` whenever a phase ends with a recommended next owner, scope, action, validation path, and risk note.
- Require an explicit checkpoint before moving from `plan` or critical challenge into `execute` or `apply-plan`, unless the user already authorized end-to-end application after the critique passes.
- Use `internal-code-review` inside `review` mode instead of duplicating the review playbook here.
- Use `internal-gateway-critical-master` as a visible critical phase when pressure testing is needed; do not duplicate its challenge logic here.
- Keep sync command centers outside this model; they retain their repo-only sync engines.

## Phase Selection

- `plan`: use when ambiguity, ownership, rollout, tradeoffs, multiple credible paths, or non-trivial repository-owned authoring must be settled before editing.
- `execute`: use when the target state is already clear, verification is concrete, and the work is deterministic local delivery or maintenance.
- `review`: use when a concrete artifact, diff, or validation result exists and the main job is defect-first evidence, findings, and fix routing.
- `critical`: use `internal-gateway-critical-master` when a proposal, plan, or decision needs pressure testing before action.

Prompt-specific intent wins over the default. A direct review request starts in `review`; a direct retained-plan application starts in `apply-plan`; a `plan-only` request stops before apply.

## Plan Mode

Plan mode owns the decision frame, assumptions, tradeoffs, selected direction, and next-step package. It does not silently become execution after the design is settled.

Use `mattpocock-grill-me` when the user asks for it, real ambiguity remains, or a non-trivial retained plan is being created, reformulated, or validated. Before asking questions, inspect the repository when the answer is recoverable from files. If the user wants to answer in bulk, provide numbered questions with a recommended answer for each; after the bulk answer, continue one question at a time only for unresolved ambiguity.

After creating a retained plan or materially reformulating one, provide a compact Decision Brief in chat. The brief is a projection, not a second canonical plan:

- 🎯 `Obiettivo`
- 🧭 `Cosa farò`
- 🧠 `Perché questa strada`
- ✅ `Vantaggi`
- ⚠️ `Rischi / protezioni`
- 🚫 `Fuori scope`
- 🧪 `Validazione`
- ⭐ `Default consigliato`
- ✋ `Decisione richiesta`

## Execute Mode

Execute mode owns clear local delivery. It may touch several adjacent files when the target state is already decided and validation is concrete. File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

For `apply-plan`, load `internal-executing-plans` and follow its repository-local `done-*` loop. The normal input is an approved retained plan under `tmp/superpowers/`; an inline plan must be converted into a retained plan or receive an explicit checkpoint before execution. `dubbi-e-domande.md` is never an executable plan file.

When ambiguity, ownership, governance, or rollout decisions become dominant, stop and use `internal-agent-support-lane-change-engine` instead of continuing as a hidden planner.

## Review Mode

Review mode owns findings, evidence gaps, regression risk, and fix routing. Findings come before summaries, and every actionable finding needs a causal layer plus a route to delivery, planning, critical challenge, or deferred follow-up.

Load `internal-code-review` for the tactical review engine whenever the task is truly review-owned.

## Staged Checkpoints

- `plan-only` stops after the plan, Decision Brief, optional critical pass, and next-step package.
- `full-cycle` may continue only through visible phase changes and the required pre-execute checkpoint.
- `apply-plan` stops for missing retained plans, inline plans without checkpoint, or blockers that `internal-executing-plans` identifies.
- `review` routes each actionable finding to delivery, planning, critical challenge, or defer.
- Critical challenge returns one of the explicit outcomes from `internal-gateway-critical-master`: `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`.

## References

- Read `references/mode-contracts.md` for detailed mode boundaries, ownership maps, and medium-task thresholds.
- Read `references/workflow-maps.md` when documenting or validating quick, planned, and audited workflows.
- Read `references/wrapper-alignment.md` when updating Copilot agent wrappers, runtime portability claims, or tests.

## Validation

- The selected entry point and active phase are explicit, or the workflow safely falls back to `plan`.
- Every staged phase includes owner, scope, anti-scope, action, validation, risk, and next checkpoint or decision.
- `internal-agent-support-next-step` is used for every user-visible transition.
- `apply-plan` uses `internal-executing-plans` and excludes `dubbi-e-domande.md`.
- `review` mode reuses `internal-code-review` instead of cloning it.
- `mattpocock-grill-me` is used for non-trivial retained plans or real clarification needs.
- Critical challenge is visible and owned by `internal-gateway-critical-master`.
- Copilot wrapper agents remain wrappers and do not re-list long workflow tables owned by this skill or its references.
