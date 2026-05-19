# Internal Contract

This document defines the rule-level invariants that future validators, sync automation, and contract tests must preserve.
Treat the current instruction architecture as the source of truth. Do not infer active policy from removed scripts, removed tests, or historical aliases.

## Principles

- Validate rules, not file size or historical implementation details.
- Treat rules as canonical and files as projections for specific consumer surfaces.
- Keep stable policy separate from volatile inventory.
- Allow useful local self-containment when it improves the consumer experience.
- Treat removed automation as historical context unless it exists on disk and is deliberately reintroduced.

## Contract Categories

### Instruction Architecture

#### `instruction-architecture-root-agents-is-entrypoint`

- Goal: keep `AGENTS.md` as the stable repository entrypoint, orientation document, and cross-surface strategic operating bridge.
- Scope:
  - root `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `.github/INVENTORY.md`
- Expected behavior:
  - root `AGENTS.md` defines the strategic role of the instruction system, the precedence model, tactical operating defaults, and the default language rule
  - root `AGENTS.md` points to `.github/copilot-instructions.md` as the repo-wide Copilot projection and to `.github/INVENTORY.md` as the exact live catalog
  - root `AGENTS.md` defines rule placement early so operational procedures do not drift into the always-on bridge
  - root `AGENTS.md` may carry compact tactical defaults for mode selection, owner visibility, validation evidence, and root-cause preference
  - root `AGENTS.md` does not carry volatile inventory, file-shape recipes, command playbooks, or long surface-specific procedures

#### `instruction-architecture-inventory-is-externalized`

- Goal: keep policy and live catalog inventory decoupled.
- Scope:
  - root `AGENTS.md`
  - `.github/INVENTORY.md`
- Expected behavior:
  - exact live asset inventory lives in `.github/INVENTORY.md`
  - policy files may point to the inventory but do not duplicate it

#### `instruction-architecture-copilot-projection-stays-meaningful`

- Goal: keep `.github/copilot-instructions.md` operationally significant for native Copilot surfaces.
- Scope:
  - `.github/copilot-instructions.md`
- Expected behavior:
  - the file stays compact, high-signal, and aligned with `AGENTS.md`
  - the file projects repo-wide behavior needed by Copilot-native flows
  - the file is not reduced to an empty shell or replaced by inventory text

#### `instruction-architecture-local-projections-stay-scoped`

- Goal: keep local instruction files concrete and consumer-aware.
- Scope:
  - `.github/instructions/**/*.instructions.md`
- Expected behavior:
  - local instructions keep only scoped, specialist, or exception-driven rules
  - useful self-containment is allowed when it helps the target surface
  - global rules are repeated locally only when the projection is deliberate and low-drift

#### `instruction-architecture-scoped-instructions-stay-matchable`

- Goal: keep scoped instructions discoverable by target path without promising universal auto-loading.
- Scope:
  - `.github/instructions/**/*.instructions.md`
  - `docs/03-local-ai-runtime-operating-model.md`
  - catalog consistency helpers and tests
- Expected behavior:
  - each active scoped instruction exposes usable `applyTo` metadata
  - non-Copilot runtimes can identify all matching instructions for a known target path and read them as manual references
  - repository-owned `internal-*` instructions and imported non-`internal-*` instructions remain eligible when their `applyTo` metadata matches
  - overlap between different glob patterns is treated as relevant co-load unless a clear conflict requires a narrower scope or explicit uncertainty
  - docs and validators describe discoverability and matching, not universal runtime enforcement

#### `instruction-architecture-knowledge-docs-keep-ownership-split`

- Goal: keep repository knowledge documents ordered and owned by the right source.
- Scope:
  - `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `docs/01-local-architecture.md`
  - `docs/02-local-repository-context.md`
  - `docs/03-local-ai-runtime-operating-model.md`
  - `.github/templates/01-architecture.md.template`
  - `.github/templates/02-repository-context.md.template`
  - sync automation and sync-contract tests
- Expected behavior:
  - `docs/01-local-architecture.md` is the repository-specific architecture contract and is scaffolded into consumers only when missing
  - `docs/02-local-repository-context.md` is descriptive local context and cannot override binding instruction policy
  - `docs/03-local-ai-runtime-operating-model.md` is source-managed runtime guidance synchronized from the standards repository
  - sync automation preserves existing consumer-local architecture and context documents after initial scaffold creation
  - `.github/templates/` remains source-side scaffold material and is not mirrored as a target catalog family

### Language Policy

#### `language-default-is-centrally-governed`

- Goal: centralize the repository language default.
- Scope:
  - root `AGENTS.md`
  - `.github/copilot-instructions.md`
  - scoped instructions, skills, and agents
- Expected behavior:
  - root `AGENTS.md` states that the default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it
  - `.github/copilot-instructions.md` may project that rule in compact form for Copilot flows
  - local files do not restate the rule in broader or stricter terms than the canonical default without declaring an explicit scoped reason

#### `language-exceptions-are-explicit-and-scoped`

- Goal: make exceptions easy to add without weakening the default.
- Scope:
  - all instruction surfaces
- Expected behavior:
  - any non-English exception names its scope and stays local to the surface that needs it
  - user chat language allowances are not treated as repository-wide authoring exceptions

### Duplication And Drift

#### `duplication-harmful-overlap-is-minimized`

- Goal: remove contradictory or drift-prone duplication.
- Scope:
  - root guidance
  - scoped instructions
  - contract docs
  - governance agents and skills
- Expected behavior:
  - contradictory copies of the same rule are removed
  - policy files do not repeat volatile inventory
  - historical recommendations do not remain framed as active requirements

  #### `duplication-thin-wrapper-entrypoints-need-content-verification`

  - Goal: prevent same-named helper files or entry points from being treated as duplicate assets without checking whether one is an intentional thin wrapper to a canonical implementation.
  - Scope:
    - repo-root helper entry points
    - `.github/scripts/**`
    - catalog review and consistency guidance
  - Expected behavior:
    - same-named files in different locations are not classified as duplicate from naming or path alone
    - review, audit, and rationalization work compares both content and operating role before recommending `DELETE` or `MERGE`
    - thin wrappers and convenience entry points to canonical implementations remain allowed when they improve operator ergonomics and do not fork the underlying logic
    - destructive deduplication requires evidence of duplicated behavior, not just matching names

#### `duplication-useful-projections-are-allowed`

- Goal: preserve local self-containment when it materially helps the consumer.
- Scope:
  - `.github/copilot-instructions.md`
  - `.github/instructions/**/*.instructions.md`
  - governance agents and skills
- Expected behavior:
  - compact repo-wide projections remain allowed
  - scoped restatements remain allowed when they improve behavior for the target surface and stay aligned with the canonical rule

#### `historical-automation-is-not-live-contract`

- Goal: prevent deleted automation from shaping active policy.
- Scope:
  - documentation
  - contract files
  - governance assets
- Expected behavior:
  - removed validators, removed sync scripts, removed contract tests, and retired bridge-era assets are not described as active requirements
  - when historical context is retained, it is clearly marked as historical rather than normative
  - future automation is rebuilt from the current contract, not from stale references

### Naming And Operating Model

#### `resource-governance-uses-supported-origin-naming`

- Goal: ensure repository resources follow the naming convention defined by origin.
- Scope:
  - skills
  - agents
  - instructions
- Expected behavior:
  - every repository-local resource uses `internal-*`
  - every external imported resource uses `<short-repo>-*`
  - every local cross-repository resource uses `local-*`

#### `resource-governance-named-resources-declare-name`

- Goal: ensure repository-owned resources that support explicit naming metadata declare it correctly.
- Scope:
  - internal skills
  - internal agents
- Expected behavior:
  - every repository-owned internal resource has a non-empty canonical identifier
  - every internal skill and agent declares a non-empty `name:`
  - every declared `name:` matches the canonical resource identifier
  - imported non-`internal-*` resources may remain verbatim

#### `resource-governance-separates-origin-from-dominant-role`

- Goal: keep prefix-based ownership distinct from dominant role so the catalog can evolve without false hierarchy drift.
- Scope:
  - governance skills and agents that describe the catalog model
- Expected behavior:
  - prefixes describe origin and ownership first, not a rigid strategic, tactical, or operational level
  - resources are evaluated on two axes: origin/ownership and dominant role
  - `superpowers-*` resources act as workflow assets and may govern strategic, tactical, or operational work
  - `internal-*` resources remain the canonical repository-owned layer and may be strategic, tactical, or operational as declared by contract
  - imported non-`internal-*` resources remain support depth by default
  - `local-*` resources remain consumer-local extensions and become strategic only when explicit local governance requires it

#### `resource-governance-wrapper-threshold-stays-explicit`

- Goal: avoid unnecessary repository-owned wrappers around imported assets.
- Scope:
  - `.github/agents/local-sync-external-resources.agent.md`
  - `.github/skills/local-agent-sync-external-resources/SKILL.md`
- Expected behavior:
  - overlap alone does not justify wrapping or replacing an imported asset
  - repository-owned wrappers or replacements are justified when they add repository-specific routing, governance, terminology, output shape, safety expectations, or a missing internal owner
  - imported assets may remain verbatim when those gaps do not exist

#### `resource-governance-canonical-operational-model-stays-explicit`

- Goal: keep the canonical repository-owned operating model clear across projections.
- Scope:
  - `.github/copilot-instructions.md`
  - canonical operational wrapper agents
  - shared operating-model skills
- Expected behavior:
  - `internal-gateway-operational-flow`, `internal-gateway-simple-task`, and `internal-gateway-critical-master` remain the canonical repository-owned skill-first gateway core
  - `internal-gateway-operational-flow`, `internal-gateway-simple-task`, and `internal-gateway-critical-master` remain the current Copilot wrapper entrypoints for that core

  - the default operational model uses direct owner selection or user-selected gateway skills with visible phases instead of a hidden repository-owned front-door router
  - `internal-gateway-operational-flow` supports `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit `plan`, `execute`, or `review` phases without creating dedicated gateway skills for each phase
  - ambiguous or mixed-shape entry fails safe to `internal-gateway-operational-flow`
  - unclear target state and multiple credible paths are explicit planning triggers
  - wrapper owners define boundaries and recommendations instead of active delegation
  - wrapper owners are not subagent-invoked by default, so hidden peer dispatch stays opt-in and explicit
  - critical challenge can return reformulation, simple, execute, review, continue-critical, or accept-with-risk outcomes
  - any future peer-automation exception between wrapper owners must be narrow, one-directional, auditably bounded, and non-mesh
  - core-skill and support-selection contracts remain explicit where the wrapper behavior depends on them

### Repository Workflow

#### `repository-workflow-github-pr-merge-and-terminal-state-reminders-stay-owned`

- Goal: keep repo-wide GitHub PR operating reminders visible without expanding the Copilot projection.
- Scope:
  - `.github/skills/internal-github-pr/SKILL.md`
  - `.github/instructions/internal-codeowners.instructions.md`
  - `.github/copilot-instructions.md`
- Expected behavior:
  - self-authored PRs under required reviews are not treated as mergeable from green checks alone
  - the GitHub PR skill tells operators to verify a qualifying non-author approval before merge
  - the GitHub PR skill prefers `gh pr merge --squash` over the default merge-commit path unless the repository clearly standardizes on another allowed merge method, and keeps `--admin` as an explicit policy-gated bypass
  - organization-wide `gh search prs` results are treated as potentially stale immediately after merge
  - repository-scoped `gh pr view --json state,mergedAt` is used to confirm terminal PR state before treating a just-merged PR as still open
  - `CODEOWNERS` placeholder-owner rules stay path-scoped instead of always-on
  - the Copilot projection does not repeat the full workflow reminder text

### Reporting

#### `reporting-completion-report-projection-stays-visible`

- Goal: keep the completion report contract visible on the surfaces that need it while keeping Copilot always-on guidance short.
- Scope:
  - `.github/copilot-instructions.md`
  - `.github/README.md`
  - relevant governance or sync agents
- Expected behavior:
  - completed runs include outcome, changed files, validation results, and remaining gaps
  - maintainer-facing docs and sync contracts may define detailed report labels such as `✅ Outcome`, `🤖 Agents`, `📘 Instructions`, `🧩 Skills`, and `📦 Other Resources`
  - supporting sections such as `🤖 Agents`, `📘 Instructions`, `🧩 Skills`, and `📦 Other Resources` are optional detail by default
  - when detail is available but omitted for token discipline, the response offers a compact follow-up and accepts number-only replies
  - the Copilot projection keeps only a compact reporting reminder unless a narrower contract requires more detail
  - root `AGENTS.md` may point to the repo-wide projection but does not need to carry the full formatting contract

#### `reporting-retained-learning-ledger-stays-governed`

- Goal: preserve retained learning without turning it into shadow policy.
- Scope:
  - root `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `LESSONS_LEARNED.md`
  - `.github/instructions/internal-lessons-learned.instructions.md`
  - `.github/skills/internal-lesson-codification/SKILL.md`
- Expected behavior:
  - repository-root `LESSONS_LEARNED.md` exists as a non-canonical learning ledger
  - completed tasks add only durable, reusable lessons that were not already codified when discovered
  - durable corrections to repeated or consequential misapplication of existing repository rules may also be retained as lessons
  - root `AGENTS.md` keeps only retained-artifact boundaries and points detailed procedures to scoped owners
  - the lesson codification skill owns the workflow that routes candidate lessons to the smallest valid canonical owner before ledger fallback
  - detailed ledger row preservation rules live in `LESSONS_LEARNED.md` entry rules
  - the scoped lessons instruction reminds editors to read and follow the file's entry rules without duplicating the full ledger procedure
  - the Copilot projection keeps only the retained-artifact principle and owner-routing reminder
  - no ledger update is required when no stable new lesson emerged
  - once a lesson is codified elsewhere, it is removed from `LESSONS_LEARNED.md` instead of being retained as a codified duplicate

### Future Automation Constraints

#### `future-automation-reads-canonical-ownership`

- Goal: ensure rebuilt validators, sync automation, and contract tests enforce the current rule ownership model.
- Scope:
  - future validator, sync, and test implementations
- Expected behavior:
  - automation reads `AGENTS.md` for cross-surface defaults and precedence
  - automation reads `.github/copilot-instructions.md` for repo-wide Copilot projection behavior
  - automation reads `.github/INVENTORY.md` for the live catalog
  - automation treats scoped instructions as local projections rather than global policy owners

#### `future-automation-preserves-scoped-exceptions`

- Goal: keep future automation compatible with local projections and explicit exceptions.
- Scope:
  - future validator, sync, and test implementations
- Expected behavior:
  - useful local projections are not rejected just because the same rule exists canonically elsewhere
  - explicit scoped exceptions are allowed when they remain local and unambiguous
  - retained tracking plans or similar follow-up artifacts live under repository-root `tmp/`

## Explicitly Out Of Scope

- exact file formatting unless a contract above requires it
- wording-level duplication that does not change behavior or drift risk
- historical migration choreography for removed assets
- any validator, sync, or test implementation detail that is not needed to preserve the current rule ownership model

## Change Rule

Add or tighten a contract only when a regression would materially break:

- rule ownership and precedence
- inventory separation
- language-default governance
- operational model clarity
- future automation rebuild safety
