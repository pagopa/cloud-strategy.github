# AGENTS.md - Skill-First AI Configuration Bridge

This file is the repository strategic operating bridge for AI configuration.
Keep it compact, stable, and free of volatile inventory or surface-specific
playbooks.

`<shared-baseline>`

This block defines guidance intended to travel as the shared baseline when this
repository projects AI configuration into other repositories.

## Rule Placement

- `AGENTS.md` must define stable repository-wide policy, precedence, tactical operating defaults, ownership boundaries, and routing anchors only.
- Do not put operational procedures, checklists, file-shape recipes, command playbooks, or tool-specific workflows here.
- Put each rule in the smallest valid owner: skills for technical baselines and workflows, agents for route UX, docs for context, validators for enforceable checks, sync owners for propagation, and owned files for their local editing rules.

## Writing Style

- Use Plain Technical English for repository-owned prose.
- Prefer short sentences, stable terms, active voice, and explicit `must`, `should`, and `may` wording.
- Keep required technical names unchanged, including paths, commands, schema fields, product names, asset names, and established repository terms.
- Do not rewrite imported upstream text that must remain verbatim.

## Role And Precedence

- `AGENTS.md` owns repository-wide defaults, precedence, rule placement, and cross-surface bridge behavior.
- `.github/copilot-instructions.md` is the repo-wide Copilot projection; keep it aligned when repository-wide defaults change.
- `.github/INVENTORY.md` owns the exact live catalog of managed AI assets; do not replace it with `AGENTS.md`.
- Sync agents own catalog prefix rules, imported-resource posture, and consumer propagation boundaries.
- `.github/skills/` owns repository-owned reusable guidance. Umbrella skills own lightweight technical-domain baselines; specialist skills and bundle references own deeper procedures.
- Use `docs/architecture.md` for repository architecture and `docs/repository-context.md` for non-policy local context.
- Use relevant skills for workflow depth, runtime consumption behavior, and reusable operating procedures.
- Consumer repositories may keep `.github/copilot-instructions.override.md` as the local exception layer; active exceptions must state scope, reason, conflict, and required disclosure.

## Context And Scope

- For runtimes without native skill loading, select the smallest relevant skill from the prompt, target path, command surface, validation signal, or repository evidence, then read that `SKILL.md` as manual context.
- Load umbrella domain skills before specialist depth when the domain is clear but the workflow depth is not yet proven.
- Co-load specialist skills or bundle references only when the task needs workflow, decision trees, domain depth, or reusable procedures.
- Use the smallest valid owner to resolve conflicts; file-owned rules and narrower skill contracts win over broad defaults inside their own scope.
- Treat `.github/agents/*.agent.md` as surface-specific wrapper projections; reusable behavior stays in skills when a runtime lacks wrapper UI.
- If no target path is known, infer obvious domains only, such as Python, GitHub Actions, Kubernetes, Docker, Markdown, or Terraform; otherwise ask for the target path before making path-scoped claims.

## Authoring Defaults

- The default authoring language for repository artifacts is English unless a narrower owned file, skill, or local exception explicitly overrides it.
- User chat may be Italian; repository-owned retained plans may use Italian when the retained-plan policy applies.
- Keep repository-owned AI configuration files as Markdown. Use XML only as runtime prompt-assembly delimiters, never as source format.
- XML-style code-span markers may delimit scope blocks in Markdown AI configuration when the content remains Markdown and the markers clarify runtime, sync, or locality boundaries.
- Do not modify `README.md` files unless the user explicitly asks.
- For vendor-owned or schema-driven surfaces, read primary documentation when correctness depends on platform semantics.
- Update validators, tests, sync discovery, or non-README technical docs when a contract, catalog family, or shared runtime behavior changes.

## Operational Ownership

- `internal-gateway-idea-brainstorming` owns same-conversation `idea -> critical -> retained plan` workflows.
- `internal-gateway-review` owns same-conversation `review -> critical -> remediation plan` workflows.
- `internal-gateway-writing-plans` owns retained-plan profile selection and recommended-consumer declaration.
- `internal-gateway-simple-task` owns direct execution and approved `compact` retained-plan consumption.
- `internal-gateway-execute-plans` owns approved `extended` retained-plan execution and final packaging.
- `internal-gateway-critical-master` owns critical challenge, pre-mortem, hidden-assumption, and failure-mode workflows.
- Copilot wrapper agents own VS Code route selection, tool scope, and manual handoff UX; support-skill loading inside one conversation is not a lane change.
- Use direct owner selection or user-selected gateway skills with visible phases. Do not add a repository-owned hidden front-door router or hidden peer dispatch.
- Light emoji markers may appear in user-facing macro-category headings when the owning skill defines them; do not use them in paths, commands, identifiers, schema fields, or copied technical values.

## Tactical Defaults

- Use `plan` mode for non-trivial repository-owned work when ambiguity, ownership, rollout, validation, or multiple credible paths remain.
- Use `execute` mode only when the target state and validation path are concrete.
- When the selected owner no longer fits, stop and make the better owner visible before continuing.
- Do not report work as complete from intent alone; cite validation evidence or name the explicit validation gap.
- Prefer root-cause fixes over symptom workarounds unless a temporary mitigation is explicitly scoped.

## Delivery And Validation

- Use least privilege and never hardcode secrets, credentials, keys, tokens, or sensitive tenant values.
- Reason from repository evidence. Do not invent runtimes, validators, sync flows, or tests.
- Prefer the simplest correct change with the smallest credible blast radius.
- For non-trivial repository-owned work, make target state, anti-scope, assumptions, tradeoffs, and validation path visible before delivery or handoff.
- Run the applicable validation that exists for changed files; when no dedicated validator exists, report the gap and use the closest check.
- Do not treat removed validators, sync scripts, contract tests, or historical aliases as active policy unless they exist on disk and are deliberately reintroduced.

## Retained Artifacts

- Keep transient planning, brainstorming, and Superpowers-generated working files out of `docs/`.
- `tmp/superpowers/` and `LESSONS_LEARNED.md` may hold retained work, but they do not replace canonical policy owners.
- Treat retained plans and retained learning as non-canonical until codified in the smallest valid owner.
- Keep file shape, execution workflow, and ledger row rules in retained-plan skills or owned files, not here.

## Token And Drift Control

- The critical always-on pair is `AGENTS.md` plus `.github/copilot-instructions.md`; its soft target is 4,000 estimated tokens measured as `ceil(UTF-8 bytes / 4)` by the validator.
- Keep duplication deliberate. Duplicate only rules that must remain visible in a specific surface and are compact enough to validate.

`</shared-baseline>`

`<standards-repository-local-rules>`

This block applies only to this standards repository. Do not treat these rules
as consumer-repository defaults without an explicit sync contract change.

## Standards Repository Role

- This repository owns the shared Copilot customization baseline, governance contracts, catalog automation, and source-side sync tooling.
- Source-managed AI assets live mainly under `.github/`; local knowledge documents live in `docs/README.md`, `docs/repository-context.md`, `docs/architecture.md`, `docs/tech.md`, and `docs/structure.md`.
- Source-side sync command centers and sync support skills own propagation behavior. Keep their procedures in the owning sync assets, not in this bridge.
- Keep consumer-facing defaults target-agnostic. Do not encode this repository's local paths, validators, or workflow checkpoints into shared guidance unless the sync contract deliberately makes them shared.

## Standards Repository Validation

- Run `make token-risks` or `python3 ./.github/scripts/detect_token_risks.py --root .` after changes that affect always-on guidance or major AI assets in this repository.
- Run the closest source-side validator for changed governance contracts, catalog families, sync behavior, or AI runtime assets.
- Address actionable source-side findings before declaring this repository's AI configuration complete.

## Standards Repository Locality

- Repo-local retained plans, brainstorming artifacts, and temporary analysis stay under `tmp/` or the owned retained-artifact locations named by skills.
- Consumer repositories may receive local scaffolds or override layers, but those target-local files remain owned by the consumer after materialization.
- Treat this block as source-local policy until sync automation or the sync contract gains explicit support for excluding or transforming it.

`</standards-repository-local-rules>`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
