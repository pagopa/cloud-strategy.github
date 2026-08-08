---
name: internal-gateway-critical-master
description: Use when a repository-owned plan, proposal, decision, or assumption set needs a full-scope critical challenge, pre-mortem, hidden-assumption test, failure-mode analysis, or lateral reframe before action, with a validated full-analysis packet as the only output.
---

# Internal Gateway Critical Master

## Referenced skills

- None.

Use this skill as the portable core for full-scope critical challenge work. The
calling gateway decides when to invoke it; this skill produces the validated
full-analysis packet and does not execute, plan, or route work.

## When to use

- A repository-owned plan, proposal, decision, or assumption set needs pressure
  before action and the result must be consumed as structured review evidence.

## When not to use

- The next step is retained planning, implementation, or evidence-first review.
- The request is for a compact summary instead of a full-scope challenge.

## Boundaries

- Challenge only. Do not edit files, run commands, access external systems,
  author retained plans, dispatch subagents, or perform active routing.
- The output is always one `internal-gateway-critical/full-analysis-v1` JSON
  packet. There is no card-only, prose-only, or early-stop output mode.

## Required input

The caller supplies `source`, `target_path`, and `target_revision` for the
current living design. `source` is `standard` or `independent`; the path is
repository-relative POSIX; the revision is a positive integer. Do not invent
missing or stale target metadata. If the caller cannot supply it, stop for the
metadata clarification needed to bind the packet safely.

Read `references/full-analysis-contract.md` before producing output. It is the
single packet-shape and outcome authority for this skill.

## Critical procedure

Run exactly three phases. Do not skip a phase and do not loop back unless new
evidence appears.

### Phase 1: Discover

- Read only the smallest evidence needed to understand the challenged proposal,
  decision, or assumption set.
- Identify the material claims, constraints, success criteria, anti-scope, and
  evidence gaps.
- Record internally what is being challenged and why it matters now.

Completion criterion: the challenged target, caller metadata, material claims,
constraints, success criteria, anti-scope, and evidence gaps are recorded.

### Phase 2: Challenge

- Select exactly three lenses from the table below based on the highest-risk
  gaps in the Discover summary.
- Lens three must be lateral: `analogy` or `reverse-assumption`.
- Apply each selected lens once.
- Apply one optional pre-mortem pass when failure modes are material and not
  covered by the selected lenses.
- Record every material finding from the full-scope challenge. Do not stop at
  the first controlling objection and do not pad the packet with weak findings.
- Ask at most one concise root question across all findings when its answer
  could materially change the critique.
- Treat mitigations as conditions to continue, not as implementation designs
  that rescue the proposal.

Completion criterion: exactly three lenses were applied, the third is lateral,
every material finding is recorded with evidence, and any material failure mode
has been represented as a finding or residual risk.

| Lens | Question | Use when |
| --- | --- | --- |
| First principles | Which claims are evidence-backed, and which are inherited assumptions? | The plan repeats local habits as if they were constraints. |
| Constraint audit | Which limits are real, and which are defaults or untested policies? | The solution seems boxed in too early. |
| Inversion | What would we do if the stated goal were reversed or forbidden? | The current path feels inevitable. |
| Counterfactual | What would be true if the rejected option were actually better? | A tradeoff has been simplified too quickly. |
| Role reversal | What would review, delivery, planning, or the user object to? | The plan optimizes one owner at another owner's cost. |
| Time shift | What breaks after one month, one sync cycle, or one consumer rollout? | The immediate change looks correct but may age badly. |
| Scope compression | What is the smallest version that preserves most value? | The plan may be overengineered. |
| Opportunity cost | What useful path is the plan excluding? | The design is safe but may be too narrow. |
| Analogy | Which solution in a different domain already solved a structurally similar problem? | The team is stuck in familiar patterns. |
| Reverse assumption | What changes if the most obvious assumption here is false? | A key claim has not been tested recently. |

Trigger a pre-mortem when at least one of these is true:

- The proposal depends on coordination across teams, systems, or sync cycles.
- A missed assumption could cause rollback, incident, or governance breach.
- The plan introduces a new operational owner, on-call rotation, or handoff.
- The change affects a production path and cannot be rolled back in under one hour.

### Phase 3: Synthesize

- Run the final consistency gate: name the strongest supported objection,
  downgrade weak claims to hypotheses, and surface unresolved uncertainty.
- Classify each material claim as `confirmed`, `inference`, or `estimate` and
  evidence quality as `strong`, `partial`, or `weak`.
- Set internal Defense to exactly one of `none`, `resolves`, `narrows`,
  `accepts-risk`, or `unanswered`; when it is not `none`, retain the strongest
  defense and its remaining vulnerability in working state.
- Select exactly one full-analysis outcome from the contract.
- Set `accepted` only when no blocking finding and no diagnostics remain.
- Set `revise-design` when at least one finding requires a design remedy.
- Set `reopen-analysis` when a blocking finding reopens assumptions or scope.
- Set `needs-clarification` only for a blocking finding tied to an unresolved
  user decision.
- Set `invalid-target` for invalid or unbound target metadata or packet input.
- Set `request-separate-review` only for an independent review request with
  `source: independent` and diagnostics.

Completion criterion: one valid packet contains the exact target binding,
source, outcome, every material finding, residual risks, and diagnostics. The
packet passes the outcome invariants in `references/full-analysis-contract.md`.

## Internal critical record

Keep the following as internal working state and project it only through the
packet:

- Challenged proposal, timing, source, target path, and target revision
- Selected lenses (exactly three; third is lateral)
- Material claims with claim class and evidence quality
- Every material finding, its evidence, blocking status, recommendation, and ID
- Strongest objection and any pre-mortem failure, causes, and conditions
- Defense classification and remaining vulnerability
- Unresolved user decisions and residual risks
- Exactly one full-analysis outcome and packet diagnostics

Preserve traceability between original intent and emerged requirements. Do not
rewrite emerged constraints as original intent. Keep material risk and decisive
uncertainty visible in the packet. The packet must contain no unsupported
numeric precision.

## Output

Emit exactly one UTF-8 JSON object conforming to
`references/full-analysis-contract.md`:

- no Markdown fences;
- no headings, preamble, appendix, prose, or emoji card;
- exactly the required top-level keys;
- unique `C-000` finding IDs and non-empty unique evidence references;
- every material finding from the challenge, not only the strongest one.

The default public path is this full-analysis packet. The packet is an internal
producer result; `/internal-gateway-idea` validates it, consolidates equivalent
findings, renders localized fields, and owns state transitions.

## Tooling

- `scripts/full_analysis.py` provides the pure packet parser, strict validator,
  and bounded `text`, `json`, and `compact` CLI views.
- The validator rejects malformed JSON, Markdown fences, unknown or missing
  keys, invalid nested values, path or revision mismatches, and outcome-invariant
  failures. An invalid packet is never a review pass.
- Keep this bundle self-contained. Do not depend on card contracts, external
  instructions, or repository-global Python modules.

## Outcome meanings

| Outcome | Use when |
| --- | --- |
| `accepted` | The full analysis has no blocking finding and no diagnostics. |
| `revise-design` | At least one material finding requires a design remedy. |
| `reopen-analysis` | A blocking finding requires assumptions or scope to be reopened. |
| `needs-clarification` | A blocking finding depends on an unresolved user decision. |
| `invalid-target` | Target metadata, packet shape, or required binding is invalid. |
| `request-separate-review` | An independent review is required and has diagnostics. |
