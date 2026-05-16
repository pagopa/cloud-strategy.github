---
name: internal-agent-operational-flow
description: Use when repository-owned work needs plan, execute, or review mode selection, especially for non-trivial work with ambiguity, ownership, rollout, validation, or multiple credible paths.
---

# Internal Agent Operational Flow

Use this skill as the portable operational core for repository-owned `plan`, `execute`, and `review` work. Copilot agents may wrap it with frontmatter, tools, and `handoffs:`, but the reusable workflow semantics live here so runtimes without agent UI can still follow the same model.

## When to use

- Repository-owned operational work needs a portable `plan`, `execute`, or `review` mode.
- A runtime such as ChatGPT, Codex plugin, or Codex CLI needs the workflow without Copilot agent UI.
- A Copilot wrapper needs the shared semantic owner for planning, delivery, or review behavior.
- A next-step package must preserve the operational transition across surfaces.

## When not to use

- The primary need is critical challenge or pre-mortem work; use `internal-agent-critical-master`.
- The work is source-side sync governance or consumer baseline propagation; use the repo-only sync owners.
- The user only needs a narrow runtime or domain skill after the operational mode is already settled.

## Core Contract

- Choose exactly one mode for the current phase: `plan`, `execute`, or `review`.
- If the mode is unclear, use `plan` as the safe fallback instead of dispatching automatically.
- Keep direct entry and manual transitions visible to the user.
- Use `internal-agent-support-lane-change-engine` when the selected mode no longer fits.
- Use `internal-agent-support-next-step` whenever a phase ends with a recommended next owner, scope, action, validation path, and risk note.
- Use `internal-code-review` inside `review` mode instead of duplicating the review playbook here.
- Keep sync command centers outside this model; they retain their repo-only sync engines.

## Mode Selection

- `plan`: use when ambiguity, ownership, rollout, tradeoffs, or non-trivial repository-owned authoring must be settled before editing.
- `execute`: use when the target state is already clear, verification is concrete, and the work is deterministic local delivery or maintenance.
- `review`: use when a concrete artifact, diff, or validation result exists and the main job is defect-first evidence, findings, and fix routing.

Do not use this skill for critical pressure testing. Use `internal-agent-critical-master` when the primary need is a challenge, pre-mortem, hidden-assumption test, or lateral reframing.

## Plan Mode

Plan mode owns the decision frame, assumptions, tradeoffs, selected direction, and next-step package. It does not silently become execution after the design is settled.

Use `mattpocock-grill-me` only as conditional support when the user asks for it, real ambiguity remains, or pre-delivery pressure would improve the plan. Before asking questions, inspect the repository when the answer is recoverable from files. If the user wants to answer in bulk, provide numbered questions with a recommended answer for each; after the bulk answer, continue one question at a time only for unresolved ambiguity.

## Execute Mode

Execute mode owns clear local delivery. It may touch several adjacent files when the target state is already decided and validation is concrete. File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

When ambiguity, ownership, governance, or rollout decisions become dominant, stop and use `internal-agent-support-lane-change-engine` instead of continuing as a hidden planner.

## Review Mode

Review mode owns findings, evidence gaps, regression risk, and fix routing. Findings come before summaries, and every actionable finding needs a causal layer plus a route to delivery, planning, critical challenge, or deferred follow-up.

Load `internal-code-review` for the tactical review engine whenever the task is truly review-owned.

## References

- Read `references/mode-contracts.md` for detailed mode boundaries, ownership maps, and medium-task thresholds.
- Read `references/workflow-maps.md` when documenting or validating quick, planned, and audited workflows.
- Read `references/wrapper-alignment.md` when updating Copilot agent wrappers, runtime portability claims, or tests.

## Validation

- The selected mode is explicit or safely falls back to `plan`.
- `internal-agent-support-next-step` is used for every user-visible transition.
- `review` mode reuses `internal-code-review` instead of cloning it.
- `mattpocock-grill-me` remains an autonomous conditional support skill.
- Copilot wrapper agents remain wrappers and do not re-list long workflow tables owned by this skill or its references.
