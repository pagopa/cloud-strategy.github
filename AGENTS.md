# AGENTS.md - Repository Operating Core

`AGENTS.md` is the primary always-on repository policy entrypoint for coding
agents in this repository. Keep it compact: it should route agents to the
nearest owner, avoid duplicated guidance, and require explicit validation.

`<shared-baseline>`

This block is the portable source baseline used to generate
`~/.agents/AGENTS.md` for cross-repository use.

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

## Progressive Disclosure

- Load only the owner, skill, contract, or documentation surface required for
  the current lane.
- Expand context only after bounded evidence leaves a material gap.

## User Alignment

- For small, deterministic, low-risk tasks, proceed after confirming target,
  owner, and validation path.
- For non-trivial, ambiguous, architectural, policy, contract, or multi-step
  work, align with the user before implementation.

## Operating Principles

- Think before acting. Confirm target, nearest owner, bounded evidence, and
  validation path before broad commands.
- Make surgical changes. Preserve user work, avoid unrelated refactors, and tie
  each edit to the requested outcome.
- Fix the controlling root cause where practical instead of layering
  workaround-only changes.
- Work toward verified outcomes. Run the closest available validation and report
  explicit gaps.

## Scope And Placement

- `AGENTS.md` owns stable repository-wide policy, precedence, tactical defaults,
  ownership boundaries, and routing anchors.
- Do not put operational procedures, checklists, file-shape recipes, command
  playbooks, or tool-specific workflows here.

## Authoring Defaults

- Use Plain Technical English for repository-owned prose.
- Prefer short sentences, stable terms, active voice, and explicit `must`,
  `should`, and `may` wording.
- Keep required technical names unchanged, including paths, commands, schema
  fields, product names, asset names, and established repository terms.
- The default authoring language for repository artifacts is English unless a
  narrower owned file, skill, or local exception explicitly overrides it.
- User chat may use the user's language; repository-owned artifacts follow the
  language rules of their closest owner.
- Keep repository-owned AI configuration files as Markdown. Use XML only as
  runtime prompt-assembly delimiters, never as source format.
- XML-style code-span markers may delimit Markdown scope blocks when they clarify
  runtime, sync, or locality boundaries.
- Do not rewrite imported upstream text that must remain verbatim.
- For vendor-owned or schema-driven surfaces, read primary documentation when
  correctness depends on platform semantics.

## Tactical Defaults

- Preserve compact working state across turns; avoid rebuilding full context
  unless new evidence invalidates the current state.
- Use bounded evidence: inspect changed sections and failing-validator context
  first, then expand only when gaps remain.

## Delivery And Validation

- Use least privilege and never hardcode secrets, credentials, keys, tokens, or
  sensitive tenant values.
- Reason from repository evidence. Do not invent runtimes, validators, sync
  flows, or tests.
- Prefer the simplest correct change with the smallest credible blast radius.
- For non-trivial repository-owned work, make target state, anti-scope,
  assumptions, tradeoffs, and validation path visible before delivery or
  handoff.
- Run the applicable validation that exists for changed files. When no dedicated
  validator exists, report the gap and use the closest check.

## Contract Discipline

- When a contract, policy, or ownership rule changes, align the owning tests,
  validators, and technical docs to the new behavior.
- Do not let stale checks or historical wording force a reverted model.

## Token And Drift Control

- `AGENTS.md` is the canonical always-on policy surface; keep it near a 4,000
  estimated-token soft target measured as `ceil(UTF-8 bytes / 4)` by the
  validator.

## graphify

Use graphify first for codebase, project, architecture, file-relationship, or
content-orientation questions when `graphify-out/graph.json` exists or graphify
is available.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"`
before doing anything else when the tool is available.

- Rules:
- Start with `graphify query "<question>"` when graphify state exists. Use
  `graphify path "<A>" "<B>"` for relationships and
  `graphify explain "<concept>"` for focused concepts.
- Dirty `graphify-out/` files after incremental updates are not a reason to skip
  graphify by default.
- If `graphify-out/wiki/index.md` exists, use it for broad navigation before raw
  source scanning.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or when
  `query`, `path`, and `explain` do not provide enough context.
- If graphify is unavailable or has no useful state, state the gap briefly and
  use the best local fallback.
- After modifying code, run `graphify update .` when graphify is available and
  repository state exists.

`</shared-baseline>`

`<standards-repository-local-rules>`

- Do not duplicate skill-owned paths, templates, workflow states, or command
  examples in this file.
- Keep volatile inventory out of this file; link to `.github/INVENTORY.md`
  instead of copying catalog entries.
- Target repositories should express local exceptions in their own nearest valid
  owner files.

## Purpose

- Orient coding agents before they read narrower files.
- Keep stable policy separate from volatile inventory; `.github/INVENTORY.md`
  owns the exact live catalog of managed AI assets.
- Keep architecture and local context in `docs/architecture.md` and
  `docs/repository-context.md`.

This block applies only to this standards repository. Do not treat these rules
as consumer-repository defaults without an explicit sync contract change.

## Standards Repository Role

- This repository owns the shared Copilot customization baseline, governance
  contracts, catalog automation, source-side sync tooling, and the source
  baseline content used to generate the global home AGENTS policy.
- Source-managed AI assets live mainly under `.github/`; local knowledge
  documents live in `docs/README.md`, `docs/repository-context.md`,
  `docs/architecture.md`, `docs/tech.md`, and `docs/structure.md`.
- Source-side sync command centers and sync support skills own propagation behavior. Keep their procedures in the owning sync assets, not in root policy.
- Keep consumer-facing defaults target-agnostic. Do not encode this repository's
  local paths, validators, or workflow checkpoints into shared guidance unless
  the sync contract deliberately makes them shared.

## Standards Repository Validation

- Run `make token-risks` or
  `python3 ./.github/scripts/detect_token_risks.py --root .` after changes that
  affect always-on guidance or major AI assets in this repository.
- Run the closest source-side validator for changed governance contracts, catalog
  families, sync behavior, or AI runtime assets.
- Address actionable source-side findings before declaring this repository's AI
  configuration complete.

## Standards Repository Locality

- Repo-local planning, brainstorming, temporary analysis, and working artifacts
  stay outside `docs/` unless a narrower owner explicitly says otherwise.
- Consumer repositories may receive local scaffolds or override layers, but those
  target-local files remain owned by the consumer after materialization.
- Treat this block as source-local policy until sync automation or the sync
  contract gains explicit support for excluding or transforming it.

`</standards-repository-local-rules>`
