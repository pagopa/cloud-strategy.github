---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be answered, edited, diagnosed, validated, or executed quickly through one lane.
---

# Internal Gateway Simple Task

## Referenced skills

- `grill-me`: mandatory pre-action interview for non-trivial simple work and one focused clarification block for simple blockers.
- `internal-gateway-idea-brainstorming`: planning owner when simple work no longer fits.
- `internal-gateway-review`: review owner when defect-first analysis becomes dominant.
- `internal-gateway-critical-master`: mandatory post-interview critical gate for non-trivial simple work and critical owner when assumptions or failure modes dominate.
- `superpowers-verification-before-completion`: final evidence gate.

Use this skill as the skill-first fast path for concrete repository-owned work.
It is single-lane and single-phase by design.

Before operational work, produce a lean Readiness Brief and name the gate
outcome. Stop for explicit user approval unless a narrower loaded skill defines
a deterministic auto-execute lane with its own zero-blocker, no-drift, and
post-run reporting gates.

`references/support-routing.md` remains the single source of truth for claim-gate owners in simple mode.

## When to use

- The outcome, target, command, or validation path is already concrete.
- One quick lane can finish: `answer`, `edit`, `diagnose`, `validate`, or `execute`.

## When not to use

- Ownership, rollout, governance, or cross-boundary tradeoffs still need a decision; use `internal-gateway-idea-brainstorming`.
- The request is defect-first review; use `internal-gateway-review`.
- The request is approved retained-plan execution; use `internal-gateway-execute-plans`.
- The primary request is pressure testing; use `internal-gateway-critical-master`.

## Simple Gate Policy

Classify every simple task before operational work as `full-gate`,
`trivial-skip`, or `escalate`.

Use `full-gate` by default for concrete simple tasks unless the task is proven
trivial and venial. Run `grill-me` first with one compact numbered block, then
run `internal-gateway-critical-master` after the user's interview response.
Before editing, executing, or finalizing, ask the user to respond first to the
`grill-me` block and then to the critical outcome.

Treat `full`, `idea`, and `complete` as depth keywords when the user applies
them to a simple task. A depth keyword forbids `trivial-skip`: run `grill-me`
first, then the critical gate. If the keyword reveals planning, review, or
pressure-testing ownership instead of simple execution, escalate to the narrow
owner named by that evidence.

Use `trivial-skip` only when all of these are true:

- the request is a local answer, tiny edit, focused read, or validator run with
  an obvious target and no material ambiguity;
- no depth keyword is present;
- no contract, routing, security, secret, tenant, governance, rollout,
  architecture, cross-file, or user-visible behavior risk is material;
- validation is obvious, local, and cheap, or the exact validation gap can be
  named before work starts.

When using `trivial-skip`, emit a short Trivial-skip proof before operational
work. The proof must name the local evidence checked, why the task is trivial
and venial, and the focused validation path or gap.

## Simple Flow

1. Inspect local files first.
2. Preserve compact working state: avoid full-context rereads unless new evidence invalidates the active lane assumptions.
3. Detect depth keywords: `full`, `idea`, or `complete`.
4. Classify the gate outcome as `full-gate`, `trivial-skip`, or `escalate`.
5. For `full-gate`, load `grill-me` and ask one compact numbered block before operational work; after the user's response, load `internal-gateway-critical-master` and ask the user to respond to the critical outcome before operational work continues.
6. For `trivial-skip`, emit the Trivial-skip proof before operational work.
7. Confirm the task still fits one quick lane.
8. Select only directly applicable skill owners and required references from prompt, target path, runtime, ownership, and validation path.
9. Build a Readiness Brief before operational work: task, lane-owner, primary assumption or risk, focused validation path, gate outcome, and explicit confirmation prompt or named auto-execute exception.
10. Stop and wait for explicit user approval before executing the lane unless the selected narrower owner declares a deterministic auto-execute lane and its preflight has zero blockers, zero ambiguous drift, and no destructive or reverse-direction action.
11. Identify mandatory applicable requirements internally before execution; do not emit a default user checklist.
12. Execute the one concrete lane.
13. Run focused validation or name the explicit gap.
14. Run a pre-close compliance audit over mandatory applicable requirements only. Delegate fresh-evidence mechanics to `superpowers-verification-before-completion`.
15. Block completion claims when mandatory applicable requirements remain unverified.
16. If architecture ownership, owner conflicts, or validation strategy are ambiguous, escalate instead of assuming a universal rule.
17. If the task stops being simple, stop and issue an escalation alert.

Escalation trigger: if evidence collection, ownership checks, or validation needs spill into multi-phase execution, route to the narrow next owner instead of expanding the fast path.

## Validation

- Work stayed single-lane and single-phase, or escalation was explicit.
- `full-gate`, `trivial-skip`, or `escalate` was named before operational work.
- Non-trivial simple work used `grill-me` before `internal-gateway-critical-master`, and depth keywords prevented `trivial-skip`.
- `trivial-skip` included evidence that the task was trivial and venial.
- Readiness Brief stayed lean, named the lane-owner and validation path, and
  included an explicit approval checkpoint or named the narrower auto-execute exception.
- Focused validation ran before completion claims, or the exact validation gap was reported.
- Auto-execute exceptions stopped on blockers, ambiguous drift, destructive actions, reverse-direction writes, or missing validation evidence.
- Completion claims were blocked when mandatory applicable requirements were still unverified.
- Output stayed concise unless a gap, exception, or escalation had to be reported.

## Common failure modes

- Treating loaded skills as automatically mandatory instead of checking applicability.
- Skipping `grill-me` and the critical gate without a Trivial-skip proof.
- Treating `full`, `idea`, or `complete` as advisory when the user meant to force the full gate.
- Expanding the Readiness Brief into a long checklist or proceeding without
  explicit user approval when no narrower auto-execute exception applies.
- Treating a generic `next_action.allowed=true` value as enough for auto-execution without checking the narrower skill's stop conditions.
- Declaring completion after code edits while mandatory applicable evidence is still missing.
- Promoting specialist requirements to universal policy without target/runtime ownership proof.
- Continuing without escalation when ownership conflicts or validation strategy remain undefined.
