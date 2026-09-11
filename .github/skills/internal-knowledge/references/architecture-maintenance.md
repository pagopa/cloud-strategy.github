# Architecture Maintenance

Use this reference to create or refresh only `docs/architecture.md` as the repository's evidence-based architecture contract.

## Repository Preflight

Resolve the repository root from the explicit target or current workspace before analysis and confirm that `docs/architecture.md` belongs to it. Read applicable repository instructions and snapshot the existing document. Determine whether the repository is single-purpose or a monorepo. Treat numbered prefixes such as `00-` and `10-`, multiple independent roots, or multiple language manifests at the top level as monorepo heuristics. Keep per-repository isolation: analyze and write one repository at a time, and do not guess a root when more than one is present. Stop before analysis on a root mismatch, unresolved instruction conflict, inaccessible target, or escaping symlink.

## Evidence

Inspect the repository layout, instructions, existing architecture document, README files, ADRs, source roots, manifests, infrastructure, workflows, tests, and validation entrypoints. Preserve still-true existing claims. Remove contradicted claims and mark material uncertainty as `Unknown / To verify`.

Classify important claims as `Documented`, `Evidenced`, `Inferred`, or `Unknown`. Cite repository paths for every claim except `Unknown`. Describe current behavior rather than a theoretical target; include intended architecture only when an authoritative source documents it. Never expose secret values.

Before drafting, analyze the repository purpose, technology stack, important paths, ownership and execution boundaries, dependency direction, supported flows, configuration sources, validation paths, visible decisions, and risks for structural AI-assisted changes. Do not create an ADR while executing the architecture workflow; report a decision that needs one and route it separately through [ADR maintenance](adr-maintenance.md).

## Reader-proportional structure

Start with `# Architecture`, a concise system orientation, the evidence-backed boundaries and relationships that matter to the stated reader outcome, validation guidance, and explicit unknowns where evidence is absent. Use only the sections needed for the stated reader outcome. Do not create empty sections.

Add purpose, current-versus-intended architecture, technology, repository map, flows, configuration, visible decisions, or agent working rules only when the section serves the stated reader outcome and has repository evidence. Use a current-versus-intended distinction only when an authoritative source supports the intended state. For a monorepo, map meaningful top-level components and describe inter-component boundaries; state whether component-specific architecture documents are warranted, but do not create them automatically.

When a selected section is useful, keep its established evidence contract: classify claims as `Documented`, `Evidenced`, `Inferred`, or `Unknown`; cite paths for every claim except `Unknown`; use status and evidence for boundaries; keep dependency directions neutral; include only evidenced runtime, build/test, or deployment flows; and record decisions with their evidence and trade-offs. Agent working rules, when included, must tell agents to read this document before structural changes, preserve existing patterns and boundaries, keep changes scoped, update the architecture document after an intentional architectural change, and report conflicts before editing. Prefer existing repository patterns over new abstractions, and do not introduce new frameworks or cross-cutting refactors without explicit approval.

Use a diagram only when it clarifies evidenced relationships for the reader. Preserve unresolved evidence as `Unknown / To verify` rather than filling a section with invented content.

## Validation and Completion

Write no application code, infrastructure, tests, workflows, instructions, prompts, ADRs, or secondary analysis artifacts. Keep the document concise, normally 150-250 lines for a single-purpose repository and no more than 400 lines for a broad monorepo, with one H1, valid Markdown, a trailing newline, no unsupported claims, and no full repository tree. Use spaced table separators `| --- | --- |`; never `|---|---|`. Before writing, pressure-test overclaims, contradictions, invented flows, false monorepo unification, and unenforceable rules; downgrade unresolved claims to an explicit `Unknown / To verify` section or note appropriate to the selected structure.

Re-read the destination immediately before writing and stop on a concurrent change. Leave an already-correct document untouched. Run safe Markdown, link, and repository validators and distinguish commands actually executed from checks only considered. Report the changed path, architecture summary, material risks or unknowns, evidence inspected, and validation performed. Do not paste the full document unless requested.
