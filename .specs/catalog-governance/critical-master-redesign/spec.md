# Redesign Critical Master

Status: ready-for-agent  
Area: catalog-governance

## Problem Statement

The user relies on Critical Master to challenge everything from code to
high-level strategy, negotiations, and personal decisions. The current skill
routes away some of those subjects and asks for a fixed lens order, layered
finding labels, and formal rerun tracking. Its report format also requires a
separate read. The risk is that producing the expected report takes priority
over finding the real problem.

The redesign must make criticism more useful, not merely shorten the prompt.
It must also preserve the review gates that already depend on the current
caller contract.

## Solution

Use one self-contained, read-only critical method that adapts to the subject.
Challenge the framing, test the proposal against real constraints and
consequences, try a meaningful reversal, and check each objection against the
strongest defense. Report only what matters, with enough evidence to judge it.

Use the simpler vocabulary by default. Where a caller requires an existing
report contract, adapt the output without changing the critical method or
requiring changes to that caller.

## User Stories

1. As a developer, I want to challenge code or a diff directly, so that I can
   test its assumptions and invariants without being sent to a different skill.
2. As a strategist, I want the critic to question the problem itself, so that I
   do not optimize a solution to the wrong problem.
3. As a negotiator, I want it to consider my alternatives and the other party's
   likely response, so that I can see where a deal may fail.
4. As a person weighing a choice, I want it to respect my stated values and show
   who bears each cost, so that I can judge the trade-offs myself.
5. As a user in a regulated domain, I want uncertainty and the need for qualified
   verification called out, so that I do not mistake critique for expert advice.
6. As a user with incomplete context, I want a useful first pass that labels its
   assumptions, so that missing data does not turn into a preliminary interview.
7. As a reader, I want to distinguish blockers, decisions, and improvements,
   so that I know what can wait.
8. As a reader, I want to see the evidence and what could overturn a finding,
   so that I can separate a demonstrated problem from a plausible concern.
9. As a decision-maker, I want a solid proposal to pass without invented
   objections, so that the critic does not create unnecessary work.
10. As a returning user, I want a requested second opinion or a focused review
    of changed evidence, so that I can see why a previous blocker still stands
    or no longer applies.
11. As a gateway owner, I want my existing review contract respected, so that I
    do not need to rewrite my gate or scoring harness.
12. As a review owner, I want to be able to call Critical Master as a
    read-only contributor without ceding the review's scope or verdict.
13. As a user requesting a critique, I want it in the language of the chat and
    without edits, so that I can act on it separately.

## Implementation Decisions

- **D1, D8 — Scope and discovery.** Remove domain-based `Route away` rules
  for direct and delegated critique. For implicit activation, distinguish
  requests to challenge premises, choices, and trade-offs from ordinary
  defect, merge-readiness, or compliance reviews. Code and existing artifacts
  remain valid subjects. Do not wire the critic into either specialist review
  workflow in this change.
- **D2, D5 — Caller compatibility.** Use a small output adapter in Critical
  Master, not a second review procedure. Honor each caller's explicit labels,
  lens count and ordering, and conclusion format. Preserve the existing Idea
  classes (`blocking-now`, `acceptance-required`, `follow-up`,
  `separate-design`, `rejected-with-reason`) and its lateral third lens;
  preserve Simple Task's exactly three lenses with a lateral third. Where
  legacy conclusions are required, map `solid` to `accepted`, `revise` to
  `revise-design`, `clarify` to `needs-clarification`, and `reframe` to
  `reopen-analysis`. Preserve legacy distinctions based on the substance of
  each finding, not its icon. Leave the callers and their scoring contracts
  unchanged. The caller or user retains scope, disposition, and acceptance.
- **D3 — Critical method.** Use at least three perspectives chosen for the
  subject, including a substantive reversal, without assigning it a fixed
  position in the default report. Question the user's framing as a hypothesis.
  Trace material failure mechanisms and second-order effects; use a
  pre-mortem when failure would be costly. Weigh reversibility and downside
  before recommending a safeguard. Test objections against the strongest
  defensible case for the proposal; require no minimum number of findings.
- **D3 — Domain and evidence.** Look for broken invariants, edge cases, and
  accidental complexity in code; incentives, alternatives, and counterpart
  reactions in strategy and negotiation; value conflicts, opportunity costs,
  and who bears them in personal or ethical choices. In regulated domains,
  distinguish critique from qualified advice. Anchor each finding to a
  concrete mechanism, indicate whether the evidence is strong, partial, or
  weak, and say what could disconfirm it. For material costs, timelines,
  impacts, or probabilities, give an evidence-supported order of magnitude
  when possible. Label estimates and explain when a quantity cannot be
  estimated without false precision.
- **D4, D5 — Default report.** Stay report-only, including when a fix is
  requested. Start from the available context without a blocking interview;
  report `failure-no-context` only if there is no analyzable subject. Lead
  with the verdict and why it follows, show the perspectives used, then
  material findings and next actions. Write in the chat language. Frame
  findings as problem, smallest useful change, and why it matters. Include
  residual risks and at most one decisive open question only when useful.
  Use 🛑 `blocker`, 🚧
  `decision-needed`, and 💹 `improvement`. Mark out-of-scope improvements as
  such; do not silently expand the work. Verdict precedence is
  `reframe > clarify > revise > solid`. A `solid` verdict can have no
  findings and is not authorization to act.
- **D6 — Reassessment.** Honor an explicit request for another critique. When
  the subject changes, focus on the change, its consequences, and unresolved
  issues. Use a short `⚪` line when useful to show what evidence closed a prior
  blocker or resolved an obvious objection. Remove the digest and suppression
  protocol; callers retain their own lifecycle rules.
- **D7 — Catalog assets.** Consolidate the method and format in the skill
  entrypoint and remove the mandatory report-format reference. Aim for about
  130–160 lines without cutting substantive guidance just to meet the target.
  Align the
  public skill metadata, agent descriptions and output instructions, and agent
  documentation across existing hosts. Preserve read-only permissions. Do
  not migrate catalog or sync paths or rewrite unrelated evaluation packs.

## Testing Decisions

- **Required contract checks for implementation.** Validate the skill bundle
  and its evaluation pack with the existing repository checks. Run the
  existing gateway and agent contract checks against the unchanged caller
  contracts. Measure the before-and-after size of the instructions loaded per
  invocation. Use the resulting size as evidence of consolidation, not proof
  of analytical quality.
- **Proposed test seam.** Prefer the public response to a representative
  request and the report consumed by each gateway. Reuse the existing
  rubric-based evaluation pack and caller scoring harness. Check that the
  critic anchors findings, preserves consequential uncertainty, and makes no
  edits. Test implicit routing separately from explicit invocation on the
  same subject. Do not assert private reasoning steps or prompt wording.
- **Optional behavioral comparison — not-run.** Compare baseline and
  redesigned responses to a code snippet or diff, an underspecified strategy,
  a negotiation, and a personal decision. Include a sound proposal that
  should not attract spurious findings and a changed-evidence case that closes
  a blocker. Judge specificity, evidence calibration, and usefulness; check
  the delegated response against each gateway contract. Structural checks
  alone do not prove runtime compliance or improved critique.

## Out of Scope

- Redesigning Idea or Simple Task, or migrating their scoring vocabulary.
- Adding a new engine or contributor step to either specialist review workflow.
- Changing source synchronization, unrelated tracker records, or Git history.
- Implementation, execution, or ticket creation as part of this publication.

## Further Notes

The Opus 5.5 counter-review identified caller compatibility as the main risk
in the initial proposal. Its accepted dispositions are F1–F7 integrated, F8
routed to separate design, and F9 rejected: keep the removal of duplicate-pass
suppression. The prior review is design evidence, not a behavioral test of
the replacement.

D9 authorizes publication of this specification and its local
`ready-for-agent` status only. It does not authorize implementation.
