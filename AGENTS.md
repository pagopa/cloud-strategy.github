# AGENTS.md - Repository Operating Core

`AGENTS.md` is the always-on, portable policy baseline for coding agents. Keep
it generic enough to reuse in any repository; keep repository-specific rules in
`AGENTS.local.md` and specialized guidance with the nearest owner.

## Precedence And Scope

- Direct user instructions win for the current task unless they require unsafe,
  destructive, or impossible behavior.
- Apply the smallest relevant owner. Narrower, target-specific rules override
  broader defaults when they conflict.
- Use only policy that exists on disk. Removed files, generated output,
  historical aliases, and past automation are not active policy.

## Skill Resolution

- The injected skill catalog is discovery evidence, not proof that a skill is
  unavailable.
- When the user or a loaded skill names a skill, search only the declared skill
  roots for that one skill before declaring it unavailable.
- For filesystem-backed skills, follow symbolic links within permission and
  trust boundaries and verify the exact resolved `SKILL.md`. A readable regular
  file proves the skill is present, even when the catalog or a non-following
  search omits it; it does not prove the runtime can invoke it.
- Read the skill and resolve its relative resources from its canonical
  directory.
- Report the concrete failure: missing skill, broken symbolic link, unreadable
  file, or unavailable execution capability. Use provider-specific discovery
  for skills that are not filesystem-backed.

## Working Agreement

- Identify the target, nearest owner, bounded evidence, and validation path
  before broad reading or commands.
- Match tool depth to task scope. Answer local naming or configuration
  questions locally, without repository-wide analysis.
- For a question limited to known files, paths, components, or file types,
  inspect only that set with targeted commands such as `rg --files` and `sed`.
  Honor explicit scope limits and skip graphify.
- Use graphify only when the answer requires broad architecture discovery,
  relationships across repository areas, dependency or data-flow tracing, or
  finding an unknown component or call path. This local-scope fast path takes
  precedence over the `## graphify` section and other broad tool triggers.
- Downshift for policy-only work. When the target state is a small declared
  policy change in known files, use only the nearest owner, the test-first rule
  in Validation And Delivery, the repository's change-scope validation, and
  adjacent tests. Load graphify, critical review, brainstorming, or external
  research only on concrete ambiguity or contradiction.
- Proceed directly for deterministic, low-risk work. Align with the user before
  non-trivial, ambiguous, architectural, policy, contract, or multi-step changes.
- For non-trivial work, state the target state, anti-scope, assumptions,
  tradeoffs, and validation path before implementation or handoff.
- Make the smallest change that fixes the controlling issue. Preserve user work
  and keep unrelated code as it is.
- Keep one active primary owner per execution lane. That owner retains material
  decisions and final acceptance; load narrower owners only when evidence shows
  they are needed.
- Ground every statement about runtimes, validators, sync flows, tests, and
  policy in repository evidence. When evidence is missing, say so explicitly.
- On a dirty working tree, snapshot the initial state, declare the task file
  allowlist, and run targeted checks before global ones. Classify global
  failures outside the allowlist as pre-existing; do not reopen
  implementation for them.

## Placement And Authoring

- Keep detailed procedures, checklists, file-shape recipes, command playbooks,
  and tool-specific workflows in their owning skills or files.
- Use Plain Technical English for repository-owned prose unless a narrower owner
  explicitly overrides it. Prefer short sentences, stable terms, active voice,
  and explicit `must`, `should`, and `may` wording.
- Keep required technical names unchanged.
- Place native tests with the component and runner that own the behavior. Use
  repository-root `tests/` only for real non-native or cross-boundary behavior.
- Treat `tmp/` as disposable support. Do not commit its contents.

## Validation And Delivery

- Route executable or evaluable behavior changes through a test-first workflow
  before implementation. Define or update the failing check before the fix.
- Name the closest executable validation early. Run it after the change and
  report unavailable checks or evidence gaps explicitly.
- When policy or a contract changes, align its owning tests, validators, and
  documentation so stale checks cannot restore the old behavior.
- Treat prose as guidance, not enforcement. Put hard guarantees in permissions,
  validators, hooks, or CI.
- Before the final answer, re-read the changed files from the working tree
  and compare them with the answer. Report only checks, content, and behavior
  that the final state contains.

### Human-Facing Responses

- A direct user-requested format or an applicable skill-owned output contract
  controls the response layout, required fields, ordering, length, visual use,
  and machine-readable shape. When a skill owns the response, use that skill's
  specialized projection and preserve its field order; apply the defaults below
  only where that narrower contract is silent.
- Lead with the outcome, and let supporting detail follow.
- Default to compact output that fits one screen, expanding on request or as
  the material's complexity requires.
- Preserve material errors, security warnings, blockers, risks, uncertainty,
  validation gaps, and the next required action in the locations defined by the
  owning skill.
- Strongly prefer Mermaid for non-trivial flows, sequences, dependencies,
  ownership models, state transitions, or multi-part comparisons when it is
  clearer than prose. Use the fewest minimal diagrams that carry the
  relationship, and state each diagram's conclusion in adjacent text.
- Group related material with headings, bullets, or tables where that aids
  scanning. When an existing retained artifact owns full evidence and decision
  history, keep that detail there and use the response for the outcome,
  material delta, risk, and next action. Create an artifact only when the work
  needs one, never solely to shorten the response.

## Protected Skill Boundary

- Imported or third-party skill bundles are protected and read-only by default.
  Where a repository uses origin prefixes, treat bundles whose names do not
  start with `internal-` or `local-` as protected.
- Invocation, wrapping, synchronization, dependency, or perceived necessity
  never implies authorization to edit a protected skill.
- Only an explicit instruction in the current user conversation naming the
  exact protected skill or path authorizes an edit.
- Authorization is limited to the requested files and purpose and does not
  carry into later turns.
- An unapproved protected-skill finding is a stop condition; do not create an
  allowlist to bypass it.

## graphify

For any question about this repo's architecture, structure, components, or how to add/modify/find
code, your first action should be `graphify query "<question>"` when `graphify-out/graph.json`
exists. Use `graphify path "<A>" "<B>"` for relationship questions and `graphify explain "<concept>"`
for focused-concept questions. These return a scoped subgraph, usually much smaller than the full
report or raw grep output.

Triggers: "how do I…", "where is…", "what does … do", "add/modify a `<component>`",
"explain the architecture", or anything that depends on how files or classes relate.

If `graphify-out/wiki/index.md` exists, use it for broad navigation. Read `graphify-out/GRAPH_REPORT.md`
only for broad architecture review or when query/path/explain do not surface enough context. Only read
source files when (a) modifying/debugging specific code, (b) the graph lacks the needed detail, or
(c) the graph is missing or stale.

Type `/graphify` in Copilot Chat to build or update the graph.

## Optional Repository-Local Policy

If `AGENTS.local.md` exists next to this file, load and apply it after this
baseline. If it does not exist, continue without error.
