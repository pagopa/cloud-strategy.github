# AGENTS.md - Repository Operating Core

`AGENTS.md` is the always-on, portable policy baseline for coding agents. Keep
it generic enough to reuse in any repository; keep repository-specific rules in
`AGENTS.local.md` and specialized guidance with the nearest owner.

## Scope And Precedence

**The narrowest applicable owner decides.**

- Local policy: when `AGENTS.local.md` exists next to this file, you must read
  it before you act and apply it after this baseline. Its rules override
  baseline defaults, subject to the limits below. When it does not exist,
  continue without error and do not create it.
- Direct user instructions win for the current task unless they require unsafe,
  destructive, or impossible behavior.
- Apply the smallest relevant owner. Narrower, target-specific rules override
  broader defaults when they conflict.
- Local policy and narrower owners must not weaken `Boundaries` or
  `Protected Skill Boundary`, or override direct user instructions.
- Keep one active primary owner per execution lane. That owner retains material
  decisions and final acceptance; load narrower owners only when evidence shows
  they are needed.
- Use only policy that exists on disk. Removed files, generated output,
  historical aliases, and past automation are not active policy.

## Boundaries

**Hard limits come first.**

- Always: keep secrets out of code and history.
- Ask first: destructive or irreversible actions, and policy or public-contract
  changes.
- Never: force-push or delete others' work. Never commit unless the user
  requests a commit in the current turn.
- A user request in the current turn authorizes its own action. An answer to
  your own question authorizes no item in `Never`: a "yes" to "shall I run the
  tests?" is not permission to commit.

## Think Before Coding

**Surface the decision before the edit.**

- Proceed: bias toward caution over speed, yet proceed directly on
  deterministic, low-risk, reversible work, and on any task where every
  reading produces the same change.
- Scope: identify the target, nearest owner, bounded evidence, and validation
  path before broad reading or commands. Match tool depth to scope and honor
  explicit scope limits. For known files or symbols, inspect only those. Search
  wider only to find an unknown component or call path. Use graph or index
  tools only when `AGENTS.local.md` or a loaded skill directs it.
- Proportion: keep a small, declared policy-only change with the nearest owner
  and its adjacent checks. A one-line change in a known config needs that file
  and one adjacent check, not a critical review. Load heavy workflows only on
  concrete ambiguity or contradiction.
- State: before editing non-trivial work, state the assumptions, target state,
  non-goals, and tradeoffs, and name what is unclear. Name the rejected reading
  in one line: `Assumption: <X>. Rejected: <Y>.` Push back when a simpler
  approach exists.
- Ask: when two plausible readings produce materially different changes, or
  when `Boundaries` require it, ask one specific question and include your
  recommendation.
- Stop: with no user channel, stop at the decision and report the blocker.
- Snapshot: on a dirty working tree, record the initial state without
  modifying it and declare the task file allowlist before editing.

## Build Simple And Surgical

**Build what the request names. Touch only what you must.**

- Write the least code that meets the goal, with the fewest abstractions,
  options, and states that internal invariants leave reachable. Add no
  abstraction for single-use code. Validate external boundaries. When 200
  lines could be 50, or a senior engineer would call it overcomplicated,
  rewrite it.
- Keep every changed line surgical: it traces to the request, matches the
  existing style even when you would write it differently, and leaves
  formatting, comments, and working code untouched, even inside touched
  functions.
- Report unrelated dead code and leave it in place unless the user asks to
  remove it. Remove only the imports, variables, and functions that your own
  change orphaned.

## Prove With Checks

**Define done as checks that can fail, then loop until they pass.**

- A check is a command with an expected result or, for prose-only work, an
  observable condition on the artifact. "Make it work" is not a check; "the
  date parser rejects 2026-13-01" is.
- Test first for executable or evaluable behavior. Fix a bug: go red by
  reproducing it with a failing check before the fix. Add validation: write
  tests for invalid inputs, then make them pass. Refactor: run the same checks
  before and after.
- For multi-step work, write the plan before editing, one check per step.
  Strong checks let you loop without asking; weak checks force clarifying
  questions.

  ```text
  1. <step> -> verify: <check>
  2. <step> -> verify: <check>
  ```

- Name the closest executable validation early, run it after the change, and
  report unavailable checks or evidence gaps explicitly.
- Run targeted checks before global ones. Treat a failure as pre-existing only
  when baseline evidence supports it, such as the same check failing on
  untouched HEAD. A failure in code the diff touches or calls is not
  pre-existing. Otherwise report its cause as unresolved.
- Ground every statement about runtimes, validators, sync flows, tests, and
  policy in repository evidence. When evidence is missing, say so.
- When policy or a contract changes, align its owning tests, validators, and
  documentation so stale checks cannot restore the old behavior.
- Treat prose as guidance, not enforcement. Put hard guarantees in permissions,
  validators, hooks, or CI.
- Before handoff, review your changes against the recorded initial state.
  Revert only your own hunks that do not trace to the request, and preserve
  all pre-existing changes. Collapse speculative options and single-use
  abstractions that your task introduced. A clarification that surfaced only
  after editing came too late: report it and confirm the diff still matches
  the clarified intent.
- Before the final answer, re-read the changed files from the working tree
  and compare them with the answer. Report only checks, content, and behavior
  that the final state contains.

### Human-Facing Responses

- A direct user-requested format or an applicable skill-owned output contract
  controls the response; apply these defaults only where it is silent.
- Lead with the outcome in compact output that fits one screen. Preserve
  material errors, security warnings, blockers, risks, uncertainty, validation
  gaps, and the next required action.
- Create an artifact only when the work needs one. When a retained artifact
  owns full evidence, keep the response to outcome, delta, risk, and next
  action.

## Skill Resolution

- The injected skill catalog is discovery evidence, not proof that a skill is
  unavailable. When the user or a loaded skill names a skill, search only the
  declared skill roots for it before declaring it unavailable.
- For filesystem-backed skills, follow symbolic links within permission and
  trust boundaries and verify the exact resolved `SKILL.md`. A readable file
  proves the skill is present, even when the catalog omits it; it does not
  prove the runtime can invoke it.
- Resolve relative resources from the skill's canonical directory. Use
  provider-specific discovery for skills that are not filesystem-backed.
  Report the concrete failure: missing skill, broken link, unreadable file, or
  unavailable execution capability.

## Protected Skill Boundary

- Imported or third-party skill bundles are protected and read-only by default.
  Where a repository uses origin prefixes, treat bundles whose names do not
  start with `internal-` or `local-` as protected.
- Only an explicit instruction in the current user conversation naming the
  exact protected skill or path authorizes an edit, limited to the requested
  files, purpose, and turn. "Update the vendored bundle's description" names
  no skill: stop. Invocation, wrapping, synchronization, dependency, or
  perceived necessity implies no authorization.
- An unapproved protected-skill finding is a stop condition; do not create an
  allowlist to bypass it.

## Placement And Authoring

- Keep detailed procedures, checklists, file-shape recipes, command playbooks,
  and tool-specific workflows in their owning skills or files.
- Use Plain Technical English for repository-owned prose unless a narrower owner
  overrides it: short sentences, stable terms, active voice, and explicit
  `must`, `should`, and `may`. Keep required technical names unchanged.
- Place native tests with the component and runner that own the behavior. Use
  repository-root `tests/` only for real non-native or cross-boundary behavior.
