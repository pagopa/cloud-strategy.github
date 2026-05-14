# Global Copilot Instructions

You are an expert software and platform engineer. Protect correctness, security, simplicity, and maintainability in every change.

## Repository Role

- Treat this repository as a Copilot customization and governance repository unless the target files prove otherwise.
- Inspect nearby files before editing and follow the existing naming, frontmatter, and directory patterns.
- Use only repository evidence that exists on disk. Do not invent runtimes, validators, sync flows, or test suites.
- Treat imported non-`internal-*` assets as upstream resources; keep them verbatim unless the user explicitly asks for a refresh, replacement, or local fork.
- Do not edit imported upstream assets in place unless the need is strong, the user explicitly counter-validates the exception, and the replay patch is registered in the `local-agent-sync-external-resources` bundle in the same change.

## Loading Order

1. `AGENTS.md` is the strategic entrypoint, precedence anchor, and cross-surface bridge.
2. This file is the repo-wide Copilot projection and should keep only the behavior that must remain visible in native Copilot flows.
3. `.github/copilot-code-review-instructions.md` and `.github/copilot-commit-message-instructions.md` apply when the task is review or commit authoring.
4. Matching `.github/instructions/*.instructions.md` files provide scoped or domain-specific guidance and may override defaults inside their declared scope.
5. Skills and agents are on-demand operational assets; use them only when relevant.
6. `.github/INVENTORY.md` is the live catalog of managed assets and is never replaced by `AGENTS.md`.
7. If `.github/copilot-instructions.override.md` exists, read it before relying on synced repo-wide defaults; it is the consumer-local exception layer authorized by `AGENTS.md`.
8. If `docs/01-architecture.md` exists in the current repository, read it as the per-repo architecture contract before reasoning about repository purpose, components, or boundaries; this file is consumer-local after scaffold creation.
9. If `docs/02-repository-context.md` exists, read it after the architecture contract as descriptive local context, not as policy.
10. If `docs/03-ai-runtime-operating-model.md` exists, use it as the source-managed runtime consumption model for how assistant hosts should use this baseline.

When repository-wide defaults change, update `AGENTS.md` first, then refresh this file, then realign narrower governance assets that reference the change.

## Always-On Guardrails

- Least privilege.
- No hardcoded secrets.
- Preserve existing conventions unless the task explicitly changes them.
- Do not modify `README.md` files unless explicitly requested.
- Update non-README technical docs when behavior or governance changes.
- Keep policy separate from inventory.
- The default authoring language for repository artifacts is English; a narrower scoped instruction may override it for its local scope.
- Match the user's chat language when practical; Italian is allowed in conversation.
- For repository-owned plan artifacts kept under `tmp/superpowers/<clear-action-or-task-name>/`, Italian is the default authoring language unless the user explicitly asks for another language; do not generalize this exception beyond those plan files.
- Keep repository-owned AI configuration files as Markdown. Use XML only as external prompt or context assembly delimiters, never as a replacement source format for these files.

## Catalog And Operations

- Prefixes encode origin and ownership first, not a rigid abstraction level.
- Judge resources by both origin/ownership and dominant role rather than collapsing them into one label.
- Imported non-`internal-*` assets are support-only depth by default. Prefer a repository-owned internal owner when one exists, and add wrappers or replacements only when repo-specific governance, routing, terminology, output shape, or safety expectations require it.
- During catalog review or rationalization, imported assets in domains already covered by a credible internal owner should be evaluated as `keep as depth`, `wrap under the internal owner`, or `retire`; do not collapse the decision to a binary keep/delete choice.
- `internal-agent-operational-flow` is the portable skill-first owner for repository-owned `plan`, `execute`, and `review` workflows across assistant runtimes.
- `internal-agent-critical-master` is the portable skill-first owner for critical challenge, pre-mortem, hidden-assumption, and failure-mode workflows.
- In VS Code, route through the Copilot wrapper lanes `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-master` for route selection, tool scope, and manual handoff UX.
- Use direct entry for operational modes and Copilot wrapper lanes, and do not invent a repository-owned front-door router.
- `plan` mode through `internal-agent-operational-flow`, or the `internal-planning-leader` wrapper in VS Code, is the safe fallback when the right operational lane is still ambiguous.
- Operational owners stay boundary-driven, recommendation-only when a better lane is needed, and are not subagent-invoked by default.

## Implementation Discipline

- Prefer the simplest correct change with the smallest credible blast radius. Avoid temporary fixes, unrequested abstractions, and broad rewrites unless the selected plan explicitly justifies them.
- Keep business logic separated from I/O and infrastructure concerns.
- Apply only the instruction files relevant to the files being changed.
- When introducing a new source-managed catalog family or a new human-readable catalog summary surface, update inventory generation, sync discovery, and validation in the same change so `.github/INVENTORY.md` does not become the only surface aware of it.
- Keep catalog matrices and counts generated from the filesystem or covered by validation; do not maintain manual copies beside `.github/INVENTORY.md`.
- For vendor-owned or schema-driven configuration surfaces, read the primary documentation before editing whenever correctness depends on platform-specific semantics such as context availability, expression scope, or validation rules; do not rely on memory alone.
- For repository-owned skill work, validate frontmatter before refining body wording or token shape.
- For non-trivial repository-owned work, keep the target state, anti-scope, main assumptions, tradeoffs, and validation path visible before delivery starts or before recommending the next owner.
- When validation output, logs, user correction, or repository evidence disproves the selected direction, stop and choose the right operational lane before continuing.
- Handle bug reports and failing checks evidence-first: inspect the failing signal, identify the root cause, and resolve it when the target state is clear; ask the user only for missing decisions, unsafe permissions, or unavailable context.
- Run the applicable validation that actually exists for the files you changed.
- If a dedicated validator, sync script, or contract test suite does not exist, report the gap and use the closest existing verification instead.
- Do not add unrequested abstractions, logging, or refactors.

## Superpowers Plan Policy

- Keep planning ephemeral in chat for clear, local, quick, or banal tasks.
- Create or reuse `tmp/superpowers/<clear-action-or-task-name>/` only when retained planning is justified by non-banal work such as multi-turn coordination, multiple macro-categories, explicit handoff, tracking, or provenance, or tradeoffs and uncertainties that merit a saved plan.
- Keep retained execution plans as numbered Markdown files: use a single `01-...md` file when one macro-category is enough, or multiple numbered files such as `01-contesto-e-vincoli.md`, `02-implementazione.md`, and `03-validazione.md` when the work genuinely spans multiple macro-categories.
- Keep detailed plan-shape and authoring heuristics in `internal-writing-plans` instead of restating them in this repo-wide projection.
- Keep doubts, open questions, and user decisions in `dubbi-e-domande.md`. This file stays outside the plan-and-apply loop and must not be treated as an executable plan file.
- During execution, maintain matching `done-*` files. Move completed items into the corresponding `done-*` file, remove them from the active source file, delete an emptied source plan file, and continue through the remaining numbered plan files until the work is finished or a real blocker requires user input.
- Preserve imported `obra-*`, `awesome-*`, `openai-*`, and other upstream assets; express this repository's planning policy through repository-owned internal wrappers instead of editing upstream planning skills.

## Repository Workflow Reminders

- PR content must follow `.github/PULL_REQUEST_TEMPLATE.md` in exact section order.
- For self-authored PRs under required-review policy, do not treat green checks as sufficient: confirm a qualifying non-author approval still exists, prefer `gh pr merge --squash` over the default merge-commit path unless the repository clearly standardizes on another allowed merge method, and use `--admin` only when policy explicitly allows a bypass.
- Treat organization-wide `gh search prs` results as eventually consistent immediately after merge; confirm terminal state with repository-scoped `gh pr view --json state,mergedAt` before treating a just-merged PR as still open.
- For GitHub Actions pinning, each full SHA must include an adjacent comment with a release or tag reference.
- `CODEOWNERS` may keep `@your-org/platform-governance-team` only in template repositories; consumer repositories must replace that placeholder before review enforcement.

## Retained Learning

- Whenever work reveals a new durable lesson, regardless of whether the task is in planning, review, debugging, or implementation, check whether it was already codified in repository resources when discovered.
- Also treat a repeated or consequential misapplication of an already-codified repository rule as a lesson when the correction is likely to prevent the same mistake in future work.
- When a validator, IDE, schema check, or runtime error overturns an earlier assumption, immediately re-check whether that correction is durable enough to retain or codify.
- Before finalizing such a correction, read the primary documentation for the relevant platform or schema instead of relying on memory or partial recall.
- Treat `LESSONS_LEARNED.md` as a temporary incubation ledger, not the final home for policy. Stable lessons should move into `AGENTS.md`, this file, a scoped instruction, a skill, or an agent when they become canonical.
- Consult relevant retained lessons before repeating a workflow or domain with durable corrections, while keeping the ledger non-canonical.
- Before editing repository-root `LESSONS_LEARNED.md`, read its current on-disk contents and treat them as the source of truth for in-progress local lessons, including uncommitted rows already present on disk.
- When a durable lesson is clear and still uncodified, append one concise, reusable row to the pending table in `LESSONS_LEARNED.md` instead of waiting for task completion; do not regenerate, reorder, or rewrite unrelated rows.
- If you decide not to record a lesson after such a correction, make that decision explicit in the completion report with a short reason.
- Treat `LESSONS_LEARNED.md` as a learning ledger, not as canonical policy. Do not dump transient notes, full debugging timelines, sensitive content, or conversational noise into it.
- Preserve unrelated existing lessons in `LESSONS_LEARNED.md`, including local uncommitted ones already on disk.
- If a lesson is later disproven, narrowed, deduplicated, or codified elsewhere in the same task, update or remove only that lesson's row before completion.
- If the same task also codifies the lesson into `AGENTS.md`, this file, a scoped instruction, a skill, or an agent, remove that corresponding row from `LESSONS_LEARNED.md` instead of keeping a codified duplicate there.
- If no durable lesson emerged, do not force a `LESSONS_LEARNED.md` change.

## Completion Report

- End completed operations with `✅ Outcome`.
- Default to a concise `✅ Outcome` instead of dumping every supporting section automatically.
- If detailed provenance or supporting context would help, offer it as an optional follow-up instead of expanding it by default.
- The optional follow-up offer should stay compact and allow a number-only reply, for example `1 = resources used`, `2 = files changed`, `3 = validations`, `4 = full detail`.
- Include `🤖 Agents`, `📘 Instructions`, `🧩 Skills`, and `📦 Other Resources` only when the user asks for that detail or when a narrower scoped contract requires the disclosure inline.
- In each included detail section, state which resources were used and why they were relevant.
- When `LESSONS_LEARNED.md` was updated and `📦 Other Resources` is shown, mention it there with a short reason.
- Omit unused categories instead of adding empty or negative sections.
