# AGENTS.md - Instruction Architecture Bridge

This file is the stable entrypoint for the repository instruction architecture.

## Role

- `AGENTS.md` is the main orientation document, the cross-surface bridge, and the precedence anchor.
- Keep this file strategic, stable, and free of volatile inventory or surface-specific playbooks.
- Treat rules as canonical here unless a narrower scoped instruction explicitly owns an exception.

## Context Loading Order

1. Use `.github/copilot-instructions.md` as the repo-wide Copilot projection.
2. Use `.github/INVENTORY.md` for the exact live catalog of instructions, skills, agents, prompts, and related assets.
3. Use `.github/instructions/` for path-specific or domain-specific projections.
4. When a runtime lacks native scoped-instruction loading and the target path is known, treat every `.github/instructions/*.instructions.md` file with matching `applyTo` metadata as relevant manual reference material.
5. Use `.github/skills/` and `.github/agents/` only when they are relevant to the current task.
6. Keep policy, projections, context, runtime guidance, and inventory separate instead of mixing them into one file.
7. If `docs/01-architecture.md` exists in the current repository, treat it as the per-repo architecture contract: read it before reasoning about repository purpose, components, system boundaries, or runtime fit, and update it in the same change when behavior, components, or boundaries move. This file is consumer-local after scaffold creation; each repository owns its own `docs/01-architecture.md`.
8. If `docs/02-repository-context.md` exists, read it after the architecture contract as descriptive local context. It may inform interpretation but must not override instruction policy.
9. If `docs/03-ai-runtime-operating-model.md` exists, treat it as the source-managed runtime consumption model for how assistant hosts should use this baseline.

## Precedence Model

- `AGENTS.md` owns repository-wide defaults, rule placement, and bridge behavior.
- `.github/copilot-instructions.md` projects the repo-wide behavior that must remain visible in native Copilot flows and must stay aligned with this file.
- `.github/copilot-code-review-instructions.md` and `.github/copilot-commit-message-instructions.md` apply when the task is review or commit authoring.
- Narrower scoped instructions may override defaults only inside their declared scope.
- `.github/copilot-instructions.override.md`, when present in a consumer repository, is the consumer-local exception layer and must state each active exception's conflict, scope, reason, and required disclosure.
- Before adding a new policy, decide whether it truly belongs at repository scope; prefer the smallest specific instruction, skill, agent, or configuration that fully owns the behavior, and promote it to `AGENTS.md` only when it changes cross-surface governance or applies across the AI configuration baseline.
- When rules conflict, prefer the smallest valid scope; if scope is equal, follow the canonical rule stated here and remove the conflicting duplicate.

## Language Default

- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.
- User chat may be Italian.
- Keep language exceptions explicit and local instead of restating broader prohibitions across the catalog.
- Repository-owned execution-plan artifacts under `tmp/superpowers/<clear-action-or-task-name>/` may default to Italian when the local planning policy applies; this exception stays local to those plan files and does not change the repository-wide English default.

## Ownership And Resource Model

- Repository-owned resources created in `cloud-strategy.github` use the `internal-*` prefix by default.
- Repository-owned resources created in other repositories use the `local-*` prefix.
- The `local-*` prefix is also reserved, inside this standards repository, for repo-owned tooling that must remain source-of-truth here and must NOT propagate to consumer repositories during sync.
- Imported upstream resources keep the `<short-repo>-<original-resource-name>` form.
- Treat prefixes as origin and ownership markers first. Do not use them as a rigid proxy for strategic, tactical, or operational level.
- Evaluate resources on two axes: origin/ownership and dominant role.
- `obra-*` resources are cross-cutting workflow assets and often support strategic framing, planning, debugging, and verification.
- `internal-*` resources are the canonical repository-owned layer and may be strategic, tactical, or operational when their contract says so.
- Imported upstream resources remain support depth by default. Overlap alone is not enough to fork or wrap them; prefer a repository-owned wrapper or replacement only when routing, governance, terminology, output shape, safety expectations, or a missing internal owner requires repo-local ownership.
- During catalog review or rationalization, imported assets in domains already covered by a credible internal owner must be evaluated as `keep as depth`, `wrap under the internal owner`, or `retire`; do not collapse that decision to a binary keep/delete choice.
- Keep imported upstream assets verbatim by default. Allow a direct in-place override only for a strong repo-specific need that the user explicitly counter-validates, and register that override in the `local-agent-sync-external-resources` skill bundle so future refreshes can replay it safely.
- When overlap exists, prefer the repository-owned internal owner as canonical and use imported depth as support unless no credible internal owner exists.

## Operational Defaults

- `internal-agent-operational-flow` is the portable skill-first core for repository-owned `plan`, `execute`, and `review` work across Copilot, ChatGPT, Codex, and other runtimes.
- `internal-agent-critical-master` is the portable skill-first core for critical challenge, pre-mortem, hidden-assumption, and failure-mode work.
- `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-master` are the current Copilot wrapper entrypoints for VS Code route selection, tool scope, and manual handoff UX.
- The operating model uses direct entry instead of a repository-owned front-door router.
- When the right mode or wrapper is unclear, prefer `plan` mode through `internal-agent-operational-flow` or the `internal-planning-leader` wrapper as the safe fallback.
- Operational owners remain recommendation-only when their boundary breaks and are not subagent-invoked by default.
- Any future automation between operational owners must be explicit, narrow, one-directional, and must not create all-to-all dispatch or nested ping-pong.
- `internal-sync-*` assets stay sync-specific and must not become second canonical homes for repository-wide policy.

## AI Configuration Editing Best Practices

- Keep repository-owned AI configuration files as readable Markdown. Use XML tags only as external prompt or context assembly delimiters when a runtime needs explicit boundaries.
- Modify the canonical owner first: `AGENTS.md` for bridge-level policy, `.github/copilot-instructions.md` for Copilot-native projection, `docs/02-repository-context.md` for descriptive local context, and `docs/03-ai-runtime-operating-model.md` for cross-runtime consumption guidance.
- Avoid duplicating the same rule across bridge, projection, context, runtime guidance, skills, and agents unless self-containment is deliberate, compact, and covered by validation.
- Keep volatile catalog paths, counts, and generated listings in `.github/INVENTORY.md`; do not move inventory into policy files.
- For vendor-owned or schema-driven surfaces, read the primary documentation before editing whenever correctness depends on platform semantics such as expression scope, context availability, validation rules, or file format behavior.
- Update validators, tests, sync discovery, and non-README technical docs in the same change when a contract, catalog family, or shared runtime behavior changes.

## Estimated Fixed-Load Token Budget

Estimated tokens are `ceil(UTF-8 character count / 4)`, measured on 2026-05-14. These counts are budget estimates, not tokenizer-exact numbers. Update this table whenever a listed always-on file changes.

| File | Target budget | Estimated tokens |
| --- | ---: | ---: |
| `AGENTS.md` | 4,500 | 3,461 |
| `.github/copilot-instructions.md` | 4,500 | 3,272 |
| `docs/01-architecture.md` | 2,500 | 1,705 |
| `docs/02-repository-context.md` | 1,500 | 964 |
| `docs/03-ai-runtime-operating-model.md` | 2,000 | 1,264 |
| `.github/README.md` | 3,500 | 2,836 |
| **Fixed-load set total** | 18,500 | 13,501 |

## Delivery Invariants

- For non-trivial repository-owned work, make the target state, anti-scope, main assumptions, tradeoffs, and validation path visible before delivery starts or before recommending the next owner.
- If validation output, logs, user correction, or repository evidence invalidates the selected direction, stop and re-select the operational lane before continuing.
- Bug reports and failing checks should be handled evidence-first: inspect the failing signal, identify the root cause, and resolve it when the target state is clear; ask the user only for missing decisions, unsafe permissions, or unavailable context.
- Prefer the simplest correct change with the smallest credible blast radius; avoid temporary fixes, unrequested abstractions, and broad rewrites unless the selected plan explicitly justifies them.
- Parallel or subagent-supported work, when allowed by the runtime and task shape, must use bounded independent scopes, visible integration, and independent verification before any completion claim.
- Do not treat removed validators, sync scripts, contract tests, or historical aliases as active policy unless they exist on disk and are reintroduced deliberately.

## Consumer Override Layer

- This standards repository owns the sync seed template at `.github/templates/copilot-instructions.override.md.template`.
- Consumer repositories may keep `.github/copilot-instructions.override.md` as the consumer-local exception layer materialized from that template by sync.
- If the target override file exists but declares no active overrides, keep the synced baseline authoritative.
- When a response follows a local override, it must say that a consumer-local exception is in effect and cite `.github/copilot-instructions.override.md`.
- Keep the target override file local in effect even when seeded by sync. Do not treat it as inventory, and do not use it to collapse the separate roles of `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md`.
- The local override layer must not redefine the ownership meaning of `internal-*`, `local-*`, or `internal-sync-*`; use it for repo-local exceptions, not for replacing the bridge model.

## Retained Learning

- Root `LESSONS_LEARNED.md` is the repository learning ledger for durable lessons discovered during repository work, regardless of phase.
- Record or codify a durable lesson as soon as it becomes clear enough to be reusable; do not wait for task completion only because the work is still in planning, review, debugging, or implementation.
- When a validator, IDE, schema check, or runtime error overturns an earlier implementation assumption, re-evaluate retained learning immediately instead of treating the correction as task-local by default.
- When correctness depends on vendor-owned workflow semantics, schema constraints, or context availability, read the primary documentation before editing or asserting that a change is valid.
- Keep `LESSONS_LEARNED.md` non-canonical. It must not replace `AGENTS.md`, `.github/copilot-instructions.md`, scoped instructions, skills, or agents.
- Treat `LESSONS_LEARNED.md` as a temporary incubation ledger: codify stable lessons into their canonical owner when ready, then remove any duplicate ledger row in the same change.
- Keep `LESSONS_LEARNED.md` append-preserving by default: preserve unrelated rows already on disk, including local uncommitted lessons, and change a specific row only when that same lesson is being codified, disproven, narrowed, or deduplicated.
- Before repeating a workflow or domain where durable corrections already exist, consult the relevant retained lessons without treating the ledger as canonical policy.
- Durable corrections to repeated or consequential misapplication of existing repository rules may also be retained as lessons.
- Keep detailed retained-learning behavior in `.github/copilot-instructions.md`; keep only the strategic boundary here.

## Volatile Artifacts

- Transient planning, brainstorming, and other Superpowers-generated working files must not be written under `docs/`.
- When such artifacts are needed inside this repository, write them under `tmp/superpowers/`.
- When retained repository-owned planning must survive the current turn, create or reuse `tmp/superpowers/<clear-action-or-task-name>/` only for non-banal, cross-turn, multi-category, handoff, tracking, provenance, or reviewable-tradeoff work.
- Keep retained execution plans as numbered Markdown files: a single `01-...md` file when one macro-category is enough, or multiple numbered files such as `01-contesto-e-vincoli.md`, `02-implementazione.md`, and `03-validazione.md` when the work spans multiple macro-categories.
- Keep unresolved questions, doubts, or user decisions in `dubbi-e-domande.md`; this file stays separate from executable plan files and remains outside the plan-and-apply loop.
- During execution, create matching `done-*` files, move completed items into them, remove them from the active numbered source file, and continue through the remaining numbered plan files until the work is finished or a real blocker requires user input.
