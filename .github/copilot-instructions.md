# Global Copilot Instructions

Protect correctness, security, simplicity, and maintainability.

`<shared-baseline>`

This block is the Copilot-native projection of the shared repository baseline.

## Critical Copilot Window

- Treat `AGENTS.md` as the strategic operating bridge, precedence anchor, tactical-default owner, and rule-placement authority.
- Keep operational procedures out of `AGENTS.md`; use skills for technical baselines, workflow depth, and reusable procedures.
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
- Keep `.github/INVENTORY.md` generated; do not turn policy, docs, or skill guidance into catalog copies.

## Context Loading

- Read `AGENTS.md` first when policy, precedence, ownership, or rule placement matters.
- Select the smallest relevant skill from the prompt, target path, command surface, validation signal, or repository evidence.
- Start with the umbrella domain skill when the domain is clear, then add specialist depth only after evidence shows it is needed.
- Load task-specific skills or references only when workflow depth, decision trees, or domain procedure is needed.
- Let the smallest valid owner win when broad guidance conflicts with file-owned rules or narrower skill contracts.
- Read `.github/copilot-instructions.override.md` before synced defaults when present.
- Use repository architecture and repository context docs for boundaries and non-policy context.
- Use relevant skills when workflow depth or runtime consumption behavior matters.

## Delivery Guardrails

- Use plan mode when ambiguity, ownership, rollout, validation, or multiple credible paths remain.
- Use execute mode only when the target state and validation path are concrete.
- If the selected owner stops fitting, pause and name the better owner before continuing.
- Do not report completion from intent alone; cite validation evidence or name the explicit gap.
- Choose the narrowest correct change that satisfies the request.
- Preserve existing conventions unless the task changes them.
- Keep policy, projection, inventory, local context, and skill-owned workflows separate.
- Allow user-selected gateway skills with visible phases; keep hidden front-door routing and hidden peer dispatch disallowed.
- Update docs, validators, tests, or sync discovery when governance contracts change.
- Read primary vendor docs before schema-driven edits.
- Handle failures evidence-first: inspect the signal, fix the root cause when clear, and ask only for unsafe or missing decisions.
- Do not add unrequested abstractions, logging, broad rewrites, or unrelated fixes.

## Retained Work

- Treat retained plans and `LESSONS_LEARNED.md` as non-canonical until codified in the smallest valid owner.
- Use dedicated retained-plan skills and lesson-codification owners for file shape, execution workflow, and ledger row rules.

## Validation And Reporting

- Run the validator that exists; use the closest check when no dedicated validator exists.
- For always-on guidance changes, run `make token-risks` or the equivalent detector and address actionable findings.
- For catalog or shared governance changes, run `make github-catalog-validation` or explain unavailable prerequisites.
- Before completion, re-check the request against the final diff and validation evidence.
- Report completed work with outcome, changed files, validation results, and remaining gaps.
- Include detailed resource sections only when the user asks or a narrower contract requires them.
- Use light emoji markers only where the owning skill defines user-facing macro-category headings; keep technical paths, commands, identifiers, and schema fields plain.

`</shared-baseline>`

`<standards-repository-local-rules>`

This block applies only to this Copilot customization and governance repository.
Do not treat it as a consumer-repository default without an explicit sync
contract change.

## Standards Repository Checkpoints

- Treat this repository as the source of the shared AI configuration baseline, catalog automation, and sync tooling.
- After inserting more than 5 items into always-on guidance files or major AI assets, run `make token-risks` or `python3 ./.github/scripts/detect_token_risks.py --root .` before creating `done-*` markers.
- Address actionable source-side findings before declaring a slice or plan file complete.
- Keep consumer-facing defaults target-agnostic; consumer repositories should use their own token-risk detector if one exists.

`</standards-repository-local-rules>`
