# AGENTS.md - Repository Operating Core

`AGENTS.md` is the primary always-on repository policy entrypoint for coding
agents in this repository. Keep it compact: it should route agents to the
nearest owner, avoid duplicated guidance, and require explicit validation.

## First Move

- Identify the requested target and nearest owner before broad reading.
- Read only the evidence needed to choose the smallest valid change and check.
- Prefer the closest executable validation; report any validation gap explicitly.

## Precedence

- Direct user instructions win for the current task unless they require unsafe,
  destructive, or impossible behavior.
- Resolve conflicts with the smallest valid owner. Treat broader files as
  fallback policy, not permission to override narrower contracts.
- Do not infer active policy from removed files, generated output, historical
  aliases, or past automation unless it exists on disk and is deliberately
  reintroduced.

## User Alignment

- For small, deterministic, low-risk tasks, proceed after identifying the
  target, nearest owner, and validation path.
- For non-trivial, ambiguous, architectural, policy, contract, or multi-step
  work, align with the user before implementation.

## Operating Principles

- Think before acting. Confirm target, nearest owner, bounded evidence, and
  validation path before broad commands.
- Make surgical changes. Preserve user work, avoid unrelated refactors, and tie
  each edit to the requested outcome.
- Fix the controlling issue where practical instead of layering workarounds.
- Work toward verified outcomes. Run the closest available validation and report
  explicit gaps.

## Scope And Placement

- `AGENTS.md` owns stable repository-wide policy, precedence, tactical defaults,
  ownership boundaries, and routing anchors.
- `.github/INVENTORY.md` is the exact live inventory of the GitHub Copilot catalog.
- `.github/instructions/**` contains platform-native Copilot projections. Portable
  agents must not discover or load these files manually or treat them as portable
  policy; native platform application remains authoritative.
- Do not put long operational procedures, detailed checklists, detailed
  file-shape recipes, command playbooks, or tool-specific workflows here.
- Short, globally safe best-practice defaults may live here when they improve
  baseline behavior without turning this file into a procedure manual.
- `tmp/` is temporary support only. Treat its contents as disposable working
  artifacts and do not commit files from `tmp/`.

## Authoring Defaults

- Use Plain Technical English for repository-owned prose unless a narrower owner
  explicitly overrides it.
- Prefer short sentences, stable terms, active voice, and explicit `must`,
  `should`, and `may` wording.
- Keep required technical names unchanged.

## Tactical Defaults

- Preserve compact working state across turns; avoid rebuilding full context
  unless new evidence invalidates the current state.
- Keep one active primary owner per execution lane; load narrower owners only
  when path, runtime, symptom, or validation evidence proves they are needed.
- Route executable or evaluable behavior changes through `/internal-tdd`
  before implementation; that skill owns test posture and sequencing.
- For bounded, token-intensive, judgment-light work, evaluate
  `/internal-low-cost-delegation`; keep material decisions and final acceptance
  with the primary owner.
- Use bounded evidence: inspect changed sections and failing-validator context
  first, then expand only when gaps remain.
- Name the validation path early; if evidence changes it, update the working
  assumption before editing.

## Delivery And Validation

- Be extremely concise in user-facing reporting without sacrificing clarity,
  correctness, safety, required evidence, or actionable next steps. Lead with
  the outcome, omit repetition and incidental process detail, and expand only
  when requested or necessary.
- Reason from repository evidence. Do not invent runtimes, validators, sync
  flows, or tests.
- For non-trivial work, make target state, anti-scope, assumptions, tradeoffs,
  and validation path visible before implementation or handoff.
- When a contract or policy changes, align the owning tests, validators, or docs
  instead of letting stale checks restore the old behavior.

## Protected Skill Boundary

- Skill bundles under `.github/skills/` whose names do not start with
  `internal-` or `local-` are protected and read-only by default.
- Invocation, wrapping, synchronization, dependency, or perceived necessity
  never implies authorization to edit a protected skill.
- Only an explicit instruction in the current user conversation naming the
  exact protected skill or path authorizes an edit.
- Authorization is limited to the requested files and purpose and does not
  carry into later turns.
- Before completion, run `.github/scripts/validate_skill_change_scope.py`
  without an allowlist, or with only the exact currently authorized bundle
  paths.
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
