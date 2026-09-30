# Architecture Maintenance

Use this reference to create or refresh only `docs/architecture.md` as the repository's evidence-based architecture contract.

## Repository Preflight

Resolve the repository root from the explicit target or current workspace before analysis and confirm that `docs/architecture.md` belongs to it. Read applicable repository instructions and snapshot the existing document. Determine whether the repository is single-purpose or a monorepo. Treat numbered prefixes such as `00-` and `10-`, multiple independent roots, or multiple language manifests at the top level as monorepo heuristics. Keep per-repository isolation: analyze and write one repository at a time, and do not guess a root when more than one is present. Stop before analysis on a root mismatch, unresolved instruction conflict, inaccessible target, or escaping symlink.

## Evidence

Inspect the repository layout, instructions, existing architecture document, README files, ADRs, source roots, manifests, infrastructure, workflows, tests, and validation entrypoints. Preserve still-true existing claims. Report defects, conflicting evidence, and verification gaps to the human. Include intended architecture only when an authoritative source documents it; report unsupported intent as a conflict rather than an open question or silently dropping it.

Classify important claims as `Documented`, `Evidenced`, `Inferred`, or `Unknown`. Cite repository paths for every claim except `Unknown`. Keep only a few unknowns when an unresolved architecture decision materially affects the reader's understanding; report other missing evidence and verification gaps to the human. Describe current behavior rather than a theoretical target. Never expose secret values.

Before drafting, analyze the repository purpose, technology stack, important paths, ownership and execution boundaries, dependency direction, supported flows, configuration sources, validation paths, visible decisions, and risks for structural AI-assisted changes. Do not create an ADR while executing the architecture workflow; report a decision that needs one and route it separately through [ADR maintenance](adr-maintenance.md).

## Reader-proportional structure

Start with `# Architecture`, a concise system orientation, the evidence-backed boundaries and relationships that matter to the stated reader outcome, validation guidance, and only decision-relevant unknowns that materially affect that outcome. Use only the sections needed for the stated reader outcome. Do not create empty sections.

Add purpose, current-versus-intended architecture, technology, repository map, flows, configuration, visible decisions, or agent working rules only when the section serves the stated reader outcome and has repository evidence. Use a current-versus-intended distinction only when an authoritative source supports the intended state. A short or narrow architecture document is complete when it serves its stated reader outcome; do not add fixed inventory, flow, or section boilerplate to make it look comprehensive. For a monorepo, map meaningful top-level components and describe inter-component boundaries; state whether component-specific architecture documents are warranted, but do not create them automatically.

When a selected section is useful, keep its established evidence contract: classify claims as `Documented`, `Evidenced`, `Inferred`, or `Unknown`; cite paths for every claim except `Unknown`; use status and evidence for boundaries; keep dependency directions neutral; include only evidenced runtime, build/test, or deployment flows; and record decisions with their evidence and trade-offs. Agent working rules, when included, must tell agents to read this document before structural changes, preserve existing patterns and boundaries, keep changes scoped, update the architecture document after an intentional architectural change, and report conflicts before editing. Prefer existing repository patterns over new abstractions, and do not introduce new frameworks or cross-cutting refactors without explicit approval.

Use a diagram only when it clarifies evidenced relationships for the reader. Keep only a few decision-relevant architecture questions in the document; report defects and other verification gaps to the human rather than turning them into unknowns or filling sections with invented content. Do not add `Last verified` stamps. Preserve any existing generated block byte-for-byte and keep authored architecture prose before its owner marker.

## Validation and Completion

Write no application code, infrastructure, tests, workflows, instructions, prompts, ADRs, or secondary analysis artifacts. Keep the document concise and reader-proportional, with one H1, valid Markdown, a trailing newline, no unsupported claims, and no full repository tree. Use spaced table separators `| --- | --- |`; never `|---|---|`. Before writing, pressure-test overclaims, contradictions, invented flows, false monorepo unification, and unenforceable rules. Report defects and verification gaps to the human; report intended behavior without an authoritative source as a conflict, not as an open architecture decision or a silent deletion.

Re-read the destination immediately before writing and stop on a concurrent change. Leave an already-correct document untouched. Run safe Markdown, link, and repository validators and distinguish commands actually executed from checks only considered. Report the changed path, architecture summary, material risks or unknowns, evidence inspected, and validation performed. Do not paste the full document unless requested.
