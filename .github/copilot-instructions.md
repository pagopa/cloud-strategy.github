# Global Copilot Instructions

Protect correctness, security, simplicity, and maintainability.

## Critical Copilot Window

- Treat `AGENTS.md` as the strategic bridge, precedence anchor, and rule-placement authority.
- Keep operational procedures out of `AGENTS.md`; use scoped instructions for path rules and skills for workflows.
- Treat this file as the Copilot-native projection; it must work when only the first 4,000 characters are read.
- Use least privilege for permissions, tokens, roles, workflows, and automation.
- Keep no hardcoded secrets: never write credentials, keys, tokens, or sensitive tenant values.
- Reason from repository evidence; do not invent runtimes, validators, sync flows, or tests.
- Apply only the instruction files relevant to the files or task.
- Run the applicable validation for changed files. Report gaps when no validator exists.
- Write repository-owned prose in Plain Technical English; preserve required technical names.
- Keep duplication deliberate; repeat only rules Copilot must see natively.

## Repository Contract

- Treat this as a Copilot customization and governance repo unless target files prove otherwise.
- Inspect nearby files and follow local naming, frontmatter, and directory patterns.
- Keep repository-owned AI configuration as Markdown; use XML only as runtime prompt delimiters.
- The default authoring language for repository artifacts is English.
- Leave `README.md` files unchanged unless the user explicitly asks.
- Do not edit imported upstream assets in place unless the need is strong, explicit, and registered.
- Keep `.github/INVENTORY.md` generated; do not turn policy, docs, or instructions into catalog copies.

## Context Loading

- Read `AGENTS.md` first when policy, precedence, ownership, or rule placement matters.
- Load every `.github/instructions/*.instructions.md` file whose `applyTo` metadata or task domain matches the target.
- Load task-specific skills only when workflow depth, decision trees, or domain procedure is needed.
- Let scoped policy win over conflicting skill workflow.
- Read `.github/copilot-instructions.override.md` before synced defaults when present.
- Use `docs/01-architecture.md` for boundaries and `docs/03-ai-runtime-operating-model.md` when runtime consumption matters.

## Delivery Guardrails

- Prefer the simplest correct change with the smallest credible blast radius.
- Preserve existing conventions unless the task changes them.
- Keep policy, projection, inventory, local context, runtime guidance, and operational workflows separate.
- Update docs, validators, tests, or sync discovery when governance contracts change.
- Read primary vendor docs before schema-driven edits.
- Handle failures evidence-first: inspect the signal, fix the root cause when clear, and ask only for unsafe or missing decisions.
- Do not add unrequested abstractions, logging, broad rewrites, or unrelated fixes.

## Retained Artifacts

- Treat retained plans and `LESSONS_LEARNED.md` as non-canonical until codified in the smallest valid owner.
- Use dedicated retained-plan skills and scoped lessons instructions for file shape, execution workflow, and ledger row rules.

## Validation And Reporting

- Run the validator that exists; use the closest check when no dedicated validator exists.
- For always-on guidance changes, run `make token-risks` or the equivalent detector and address actionable findings.
- For catalog or shared governance changes, run `make github-catalog-validation` or explain unavailable prerequisites.
- Before completion, re-check the request against the final diff and validation evidence.
- Report completed work with outcome, changed files, validation results, and remaining gaps.
- Include detailed resource sections only when the user asks or a narrower contract requires them.
