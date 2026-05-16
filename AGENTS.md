# AGENTS.md - Instruction Architecture Bridge

This file is the repository constitution for AI configuration. Keep it short,
stable, strategic, and free of volatile inventory or surface-specific playbooks.

## Writing Style

- Use Plain Technical English for repository-owned prose: plain language with light controlled-language principles.
- Prefer short sentences, stable terms, active voice, one rule per bullet, and explicit `must`, `should`, and `may` wording.
- Keep required technical names unchanged, including paths, commands, schema fields, product names, asset names, and established repository terms.
- Do not rewrite imported upstream text that must remain verbatim.

## Role And Precedence

- `AGENTS.md` owns repository-wide defaults, precedence, rule placement, and cross-surface bridge behavior.
- `.github/copilot-instructions.md` is the repo-wide Copilot projection; keep it aligned when repository-wide defaults change.
- `.github/INVENTORY.md` owns the exact live catalog of managed AI assets; do not replace it with `AGENTS.md`.
- `.github/instructions/*.instructions.md` owns scoped path or domain rules; a matching narrower scope overrides broad defaults only inside that scope.
- Use `docs/01-architecture.md` for repository architecture, `docs/02-repository-context.md` for non-policy local context, and `docs/03-ai-runtime-operating-model.md` for runtime consumption guidance.
- Use the smallest valid owner for a rule. If scope is equal, follow the canonical rule here and remove the conflicting duplicate.
- Consumer repositories may keep `.github/copilot-instructions.override.md` as the local exception layer; active exceptions must state scope, reason, conflict, and required disclosure.

## Scoped Context Loading

- For runtimes without native scoped-instruction loading, match known target paths against `.github/instructions/*.instructions.md` `applyTo` metadata before editing, reviewing, or asserting scoped policy.
- Read every matching instruction as manual context, including co-loaded imported and `internal-*` instructions.
- Treat scoped instructions as the baseline for matching paths, domains, or file families.
- Prefer the narrower scoped instruction only for direct path-specific conflicts.
- Co-load relevant skills when the task needs workflow, decision trees, domain depth, or reusable procedures.
- When scoped instructions and skills both apply, use them together; applicable policy and scoped rules win if a skill procedure conflicts.
- Use docs for descriptive context and runtime models, not as primary policy.
- If no target path is known, infer obvious domains only, such as Python, GitHub Actions, Kubernetes, Docker, Markdown, or Terraform; otherwise ask for the target path before making path-scoped claims.

## Authoring Defaults

- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.
- User chat may be Italian; repository-owned execution-plan artifacts under `tmp/superpowers/<clear-action-or-task-name>/` may use Italian when the retained-plan policy applies.
- Keep repository-owned AI configuration files as Markdown. Use XML only as runtime prompt-assembly delimiters, never as source format.
- Do not modify `README.md` files unless the user explicitly asks.
- For vendor-owned or schema-driven surfaces, read primary documentation when correctness depends on platform semantics.
- Update validators, tests, sync discovery, or non-README technical docs when a contract, catalog family, or shared runtime behavior changes.

## Resource Ownership

- Repository-owned resources created in this standards repository use the `internal-*` prefix by default.
- Repository-owned resources created in consumer repositories use `local-*`; in this standards repository, `local-*` also marks source-owned tooling that must not propagate during sync.
- Imported upstream resources keep the `<short-repo>-<original-resource-name>` form.
- Prefixes encode origin and ownership first, not a rigid strategic, tactical, or operational level.
- Imported assets are support depth by default. Prefer a repository-owned internal owner only when routing, governance, terminology, output shape, safety expectations, or a missing owner requires it.
- Keep imported upstream assets verbatim by default. Allow a direct in-place override only for a strong repo-specific need that the user explicitly counter-validates, and register it in the `local-agent-sync-external-resources` bundle.
- Use `.github/INVENTORY.md` for exact paths, counts, and generated catalog listings.

## Operational Ownership

- `internal-agent-operational-flow` owns the reusable `plan`, `execute`, and `review` mode semantics.
- `internal-agent-critical-master` owns critical challenge, pre-mortem, hidden-assumption, and failure-mode workflows.
- Copilot wrapper agents own VS Code route selection, tool scope, and manual handoff UX; reusable behavior stays in skills.
- Use direct owner selection. Do not add a repository-owned front-door router or hidden peer dispatch.
- When the right owner is unclear, fail safe to `internal-planning-leader` or `plan` mode through `internal-agent-operational-flow`.

## Delivery And Validation

- Use least privilege and never hardcode secrets, credentials, keys, tokens, or sensitive tenant values.
- Reason from repository evidence. Do not invent runtimes, validators, sync flows, or tests.
- Prefer the simplest correct change with the smallest credible blast radius.
- For non-trivial repository-owned work, make target state, anti-scope, assumptions, tradeoffs, and validation path visible before delivery or handoff.
- Run the applicable validation that exists for changed files; when no dedicated validator exists, report the gap and use the closest check.
- Do not treat removed validators, sync scripts, contract tests, or historical aliases as active policy unless they exist on disk and are deliberately reintroduced.

## Retained Plans

- Keep transient planning, brainstorming, and Superpowers-generated working files out of `docs/`; use `tmp/superpowers/` inside this repository.
- Create or reuse `tmp/superpowers/<clear-action-or-task-name>/` only for non-banal, cross-turn, multi-category, handoff, tracking, provenance, or reviewable-tradeoff work.
- Keep retained execution plans as numbered Markdown files: use one `01-...md` file for one macro-category, or multiple numbered files such as `01-contesto-e-vincoli.md`, `02-implementazione.md`, and `03-validazione.md` for multiple macro-categories.
- Keep unresolved questions in `dubbi-e-domande.md`; it stays outside the executable plan loop.
- During execution, create matching `done-*` files, move completed items into them, remove them from the active numbered file, delete emptied source plan files, and continue through the remaining numbered plan files until finished or genuinely blocked.

## Retained Learning

- Root `LESSONS_LEARNED.md` is the repository learning ledger for durable lessons discovered during repository work.
- Keep `LESSONS_LEARNED.md` non-canonical; it must not replace `AGENTS.md`, `.github/copilot-instructions.md`, scoped instructions, skills, or agents.
- Treat `LESSONS_LEARNED.md` as a temporary incubation ledger: codify stable lessons into the smallest canonical owner when ready, then remove any duplicate ledger row in the same change.
- Retain durable corrections to repeated or consequential misapplication of existing repository rules when they are not already codified.
- Use `LESSONS_LEARNED.md` entry rules for detailed ledger-editing behavior; keep only the strategic boundary here and short Copilot-native reminders in `.github/copilot-instructions.md`.

## Token And Drift Control

- The critical always-on pair is `AGENTS.md` plus `.github/copilot-instructions.md`; its soft target is 4,000 estimated tokens measured as `ceil(UTF-8 bytes / 4)` by the validator.
- Do not maintain token-count tables in `AGENTS.md`; keep exact estimates in validator output, reports, or tests.
- Run `make token-risks` or `python3 ./.github/scripts/detect_token_risks.py --root .` after changes that affect always-on guidance or major AI assets.
- Keep duplication deliberate. Duplicate only rules that must remain visible in a specific surface and are compact enough to validate.
