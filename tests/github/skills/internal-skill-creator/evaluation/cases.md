# Fixed Evaluation Cases

## Runtime evidence gap

- Runtime: unavailable.
- Reason: this repository has no executable resolver for skill prose or model invocation.
- Interpretation: each observed decision below is a human-reviewed contract classification, not a runtime invocation pass.

## Positive: multi-file inventory

Prompt: Inventory the named skill files and map their consumers across selectors,
validators, tests, and metadata. Return bounded evidence and leave policy and
acceptance decisions with the parent.

Expected decision: Delegate with mode `read`.

Evidence to inspect: the multi-file inventory row in the creator matrix,
`fixtures/valid-read-brief.json`, and the explicit-mode fixture test.

Observed decision: Human review classifies this as eligible for `read`; runtime
invocation evidence is unavailable.

## Positive: bounded draft

Prompt: Draft one artifact at the exact declared path after the outline,
metadata shape, acceptance checks, and validation commands are fixed. The parent
will review the semantic content.

Expected decision: Delegate with mode `plan`.

Evidence to inspect: the bounded-draft row in the creator matrix,
`fixtures/valid-plan-brief.json`, `fixtures/worker-output.md`, and
`fixtures/valid-plan-result.json`.

Observed decision: Human review classifies this as eligible for `plan`; runtime
invocation evidence is unavailable.

## Positive: one-artifact write

Prompt: Produce one bounded implementation artifact at the exact declared path
from fixed evidence and checks. The parent will run independent validation and
accept or reject the result.

Expected decision: Delegate with mode `write`.

Evidence to inspect: the one-artifact row in the creator matrix,
`fixtures/valid-write-brief.json`, and the result-binding tests.

Observed decision: Human review classifies this as eligible for `write`; runtime
invocation evidence is unavailable.

## Near-miss: single command or obvious edit

Prompt: Run one command or make one obvious local edit that the parent could
complete directly.

Expected decision: Perform the work locally; do not invoke a worker.

Evidence to inspect: the local-only admission rule and the value-gate tests.

Observed decision: Human review keeps this local; runtime invocation evidence is
unavailable.

## Near-miss: unresolved material decision

Prompt: Choose an unresolved policy, boundary, authority, acceptance, or scope
decision while drafting the skill.

Expected decision: Keep the work with the parent or stop for the missing
decision; do not invoke a worker.

Evidence to inspect: the parent-owned decision list, the local-only admission
rule, and the incomplete-brief fixture.

Observed decision: Human review keeps this with the parent or blocks it; runtime
invocation evidence is unavailable.

## Competing owner: Copilot agent

Prompt: Create or materially revise a Copilot agent under `.github/agents/`.

Expected decision: Route to `/internal-agent-creator`, not
`/internal-skill-creator`.

Evidence to inspect: the competing-owner rule and the protected-path boundary.

Observed decision: Human review routes this to `/internal-agent-creator`; runtime
invocation evidence is unavailable.
Review status: accepted with a runtime evidence gap.
