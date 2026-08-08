---
name: internal-low-cost-delegation
description: Use when bounded, token-intensive work requires little independent judgment and a parent can close every material decision first.
---

# Internal Low-Cost Delegation

## When to use

Use this skill when a parent owns the objective, scope, decisions, output
shape, destinations, validation, and stop conditions, while the remaining work
is high-volume generation or evidence handling with little independent
judgment. Read `references/task-packet.md` for the packet and result contract,
then read `references/runtime-adapters.md` for platform prerequisites.

## When not to use

Do not use this route for architecture, policy, security, ambiguous scope,
trade-offs, final acceptance, autonomous implementation, trivial work whose
packet overhead erases the saving, or work that requires the worker to choose a
model, agent, destination, or validation path. Keep those decisions with the
parent.

## Core contract

Skill text is routing guidance. It does not guarantee that a named agent, model,
effort level, or runtime invocation is available.

Follow this ordered workflow:

1. Test whether the work is bounded, token-intensive, and judgment-light. If
   eligible, delegate the bounded slice rather than performing it in the parent.
2. Close every material decision in the parent before delegation.
3. Select the exact native route: `internal-low-cost-copilot` for Copilot or
   `internal-low-cost-codex` for Codex, then verify its model and effort
   prerequisites.
4. Build a complete task packet using the local task-packet reference.
5. Invoke only the selected native route and wait for its result.
6. Validate status, changed paths, artifact shape, and every declared command.
7. Let the parent accept, revise, discard, or apply the packet's explicit
   fallback.

Never silently substitute another worker, model, effort level, route, or
destination. Never use nested delegation. The worker may produce and persist
only artifacts that the complete packet authorizes; it may not own material
implementation, architecture, policy, security, scope, or acceptance
decisions.

## Eligibility and packet boundary

The parent must provide the complete packet before the worker reads beyond the
declared inputs or writes anything. The packet must name one native worker
exactly, lock decisions and structure, declare allowed and forbidden paths,
list validation commands, set limits, and identify escalation conditions. An
incomplete or contradictory packet returns `needs-parent` before writes.

The worker may perform evidence collection, summarization, extraction,
repository exploration, log or validator analysis, mechanical text
transformation, and writing an already-structured plan when those actions are
explicitly inside the packet. It must stop on any new material decision,
undeclared command, unexpected path, unsafe operation, or unavailable required
capability.

## Runtime route and fallback

Use the truthful platform adapters in `references/runtime-adapters.md`. Verify
the runtime-reported model and effort instead of inferring a provider slug.
When the selected native worker, model, effort, or invocation cannot be
verified, show the parent fallback explicitly and do not silently continue on a
substitute.

## Result and parent review

Require the worker's `completed`, `needs-parent`, or `blocked` result shape
from `references/task-packet.md`. Check the reported artifacts against the
packet's write scope, rerun or inspect every declared validation, and compare
unexpected changes before the parent accepts the result. The parent retains
the final decision to accept, revise, discard, or use the explicit fallback.

## Safety boundary

Keep this bundle self-contained. Do not materialize runtime-home files,
expand the packet, alter worker authority, or turn an unavailable external
capability into a local pass. Record model-selection evidence and unresolved
external or human-review obligations separately from local validation.
