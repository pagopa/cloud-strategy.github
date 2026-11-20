# Authoring and Proportional Evaluation

## Intent contract

Recover known answers from the request and repository evidence. Capture the
capability, invocation conditions, expected output, constraints, dependencies,
success criteria, validation path, and anti-scope.

## Creator delegation matrix

Apply the delegation gate in `SKILL.md` first. This matrix maps eligible
creator tasks to a mode.

| Creator task | Mode | Expected output | Write scope | Parent acceptance |
| --- | --- | --- | --- | --- |
| Multi-file inventory or consumer mapping | `read` | bounded analysis/evidence | empty | Every named path and consumer class is covered; no unresolved decision is silently inferred. |
| Evidence inventory across known sources | `read` | bounded analysis/evidence | empty | Evidence refs resolve and authority remains with the parent. |
| Draft after outline, metadata, acceptance, and validation are fixed | `plan` | one artifact at one exact path | one exact draft path | Parent reviews semantic content and applies or accepts it. |
| One bounded implementation artifact | `write` | one artifact | one exact file or artifact path | Parent runs independent validation and accepts the result. |
| Bounded validation set with multiple observable checks | `read` | validation evidence | empty | All declared checks and pass signals are present. |

Use one worker, one brief, and one result. Default to one attempt. A corrective
retry requires new evidence and a concrete correction target, and it must carry
a changed brief. Cosmetic, punctuation, prose-only, and semantic disagreement do
not reopen the worker.
Direct worker writes are limited to one exact declared artifact; the parent
reviews and accepts it. The worker never edits the creator contract, inventory,
approval records, protected bundles, or broad directories.

## Bundle evidence

For a bundle change, inspect every existing sibling under `references/`,
`scripts/`, `assets/`, and `agents/openai.yaml`, or record why a sibling is
intentionally unaffected. Checked-clean surfaces are evidence, not findings.

## Consumption and ownership

Distinguish a file's existence from selection or consumption through routing,
cross-skill calls, validators, tests, inventory, or sync. Keep generic
analysis-only review outside this creator.

After the parent locks the required inventory, consumer map, outline, metadata
shape, or evaluation command, it may invoke `internal-luna-executor` through
`/internal-subagent-contract` with one `DelegationBrief` v1. The caller verifies
the adapter-composed `WorkerResult` v1 and caller-owned `VerificationReceipt`
v1; unobserved worker validation and budget data remain claims or unavailable
evidence. When timeout, interruption, executor unavailability, or missing
terminal output prevents a worker payload, the caller records a
`LifecycleRecord` and creates neither a synthetic `WorkerResult` nor a
`VerificationReceipt`. Trigger, boundary, policy, scope, retry choice,
independent validation, acceptance, semantic review, closeout, and subjective
authoring decisions remain with the parent.

## Lifecycle and retirement

Check compatibility, periodic maintenance, replacement, propagation, and
retirement readiness when the change affects them. Retirement must leave no
hollow references or unmanaged catalog fallout.

## Propagation and proof

Name each affected inventory, sync, validator, and test surface. A report or
output-contract change propagates to three surfaces: the SKILL.md contract,
`agents/openai.yaml`, and the paired `.github/agents/<name>.agent.md` when one
exists. Prefer the smallest deterministic proof and record unavailable proof
as a gap.

## Evaluation selection

Classify each candidate branch as applicable, skipped, or blocked. Objective
file transformations and fixed workflows use executable checks. Subjective
writing, design, and judgment work use human review.

| Change surface | Required evidence |
| --- | --- |
| Frontmatter, metadata, paths, references | Parsed structural validator |
| Script, CLI, parser, generator | Executable test with fixtures |
| Stable public output | Producer and consumer test |
| LLM routing or trigger | Executable resolver or concrete evaluation cases |
| Mandatory rule moved behind a conditional reference | Treat as behavioral reachability change and evaluate the affected branch |
| Subjective instructional prose | Human review with an explicit evidence gap when runtime evaluation is unavailable |
| Editorial wording that preserves behavior | Markdown and token validation only |

Raw instructional wording is not an executable or evaluable seam. Do not
manufacture wording tests when a change has no parser, executable consumer,
public protocol, or concrete evaluation case.

## Evaluation packs and baselines

Use [`eval-packs.md`](eval-packs.md) to define requirements, cases, trigger
queries, frozen criteria, and evidence states. Use
[`grading-and-analysis.md`](grading-and-analysis.md) to grade artifacts and
interpret comparisons. For a new skill, compare with the same task without it
when the host can isolate that condition. For a material revision, compare
with a frozen snapshot under `tmp/`.

## Evidence and human review

For each applicable branch, record the prompt or fixture, expected and observed
behavior, review method, and status. Present subjective outputs to the user
before changing them from agent judgment alone. Generalize feedback; do not
optimize only for sampled prompts.

## Iteration stop conditions

Stop when the accepted prompts and validators pass, the user accepts subjective
outputs, or another iteration adds no decision-relevant evidence. Keep required
evidence gaps blocked.

## Rule shape and merging

Apply this pass to every workflow section you author or revise.

- Principle: open the section with one line the agent can repeat, such as
  "Freeze criteria before reading outputs."
- Trigger word: open each conditional bullet with the condition word, such as
  `Ask:`, `Stop:`, or `On a dirty tree:`. State invariants as direct
  imperatives.
- Concreteness: replace a vague bound with a threshold, template, or example a
  reader can check, such as "under 30 lines" or `1. <step> -> verify: <check>`.
  Add the reason only when no file, config, or command reveals it.
- Example independence: write examples that differ from every eval prompt in
  the bundle's pack. An example that mirrors a prompt teaches the case, not the
  rule, and inflates the score.
- Merging: merge two rules only when they share a trigger and an authorization
  regime. An unconditional ban, a per-turn request, and an exact-path
  authorization are three regimes. Before a merge, map the cases that cover
  each rule and run or review them after the merge.

Detailed writing technique, such as leading words, negation, and no-op tests,
lives in `/mattpocock-writing-for-agents`; this section takes precedence.

## Portability and invocation contract

`SKILL.md` frontmatter allows only `name`, `description`, `metadata`, `license`,
and `compatibility`. `name` matches the bundle directory name. Invocation
policy goes to `agents/openai.yaml` under
`policy.allow_implicit_invocation`. Provenance fields (`source`, `risk`,
`date_added`, and `revision`) go under `metadata`. The validator blocks
non-portable fields.

Write each frontmatter value so strict YAML reads it as one string. Wrap the
whole value in double quotes, or use a `>-` folded block, when it contains a
colon followed by a space, ends with a colon, contains a space followed by
`#`, or starts with a YAML indicator such as `` ` ``, `@`, `%`, `&`, `*`,
`!`, `#`, `-`, or `?`. Trigger-first
descriptions often hit this with a list after a colon, for example
`Use when the problem is X: A, B, or C.` Copilot then reports
`mapping values are not allowed` and skips the skill. A lenient host parser
can accept the same file, so a host validator pass is not proof;
`scripts/check_skill_frontmatter.py` is the gate.
