# Architecture Maintenance

Use this reference to create or refresh only `docs/architecture.md` as the repository's evidence-based architecture contract.

## Repository Preflight

Resolve the repository root from the explicit target or current workspace before analysis and confirm that `docs/architecture.md` belongs to it. Read applicable repository instructions and snapshot the existing document. Determine whether the repository is single-purpose or a monorepo. Treat numbered prefixes such as `00-` and `10-`, multiple independent roots, or multiple language manifests at the top level as monorepo heuristics. Keep per-repository isolation: analyze and write one repository at a time, and do not guess a root when more than one is present. Stop before analysis on a root mismatch, unresolved instruction conflict, inaccessible target, or escaping symlink.

## Evidence

Inspect the repository layout, instructions, existing architecture document, README files, ADRs, source roots, manifests, infrastructure, workflows, tests, and validation entrypoints. Preserve still-true existing claims. Remove contradicted claims and mark material uncertainty as `Unknown / To verify`.

Classify important claims as `Documented`, `Evidenced`, `Inferred`, or `Unknown`. Cite repository paths for every claim except `Unknown`. Describe current behavior rather than a theoretical target; include intended architecture only when an authoritative source documents it. Never expose secret values.

Before drafting, analyze the repository purpose, technology stack, important paths, ownership and execution boundaries, dependency direction, supported flows, configuration sources, validation paths, visible decisions, and risks for structural AI-assisted changes. Do not create an ADR while executing the architecture workflow; report a decision that needs one and route it separately through [ADR maintenance](adr-maintenance.md).

## Canonical Structure

Start with `# Architecture`. Use exactly these level-two headings in this order:

1. `## 1. Purpose`
2. `## 2. System overview`
3. `## 3. Current vs intended architecture`
4. `## 4. Technology stack`
5. `## 5. Repository map`
6. `## 6. Architectural boundaries`
7. `## 7. Dependency rules`
8. `## 8. Key flows`
9. `## 9. Configuration and environment`
10. `## 10. Testing and validation`
11. `## 11. Architectural decisions visible in the repo`
12. `## 12. AI-agent working rules`
13. `## 13. Last verified`
14. `## 14. Unknown / To verify`

Apply these section contracts:

- Keep section 2 to a 5-10 line orientation and add a diagram only when it clarifies evidenced relationships.
- In section 3 use `Area`, `Current architecture`, `Intended architecture`, `Status`, and `Evidence`; populate intended architecture only from an authoritative source.
- In section 4 use `Area`, `Technology`, `Status`, and `Evidence`.
- In section 5 use `Path`, `Responsibility`, and `Notes`, listing only important paths.
- In section 6 give important boundary claims a status and evidence path.
- In section 7 use `### Allowed direction` and `### Avoid / forbidden`; send unsupported rules to section 14.
- In section 8 use only the evidenced subsections among `### Runtime flow`, `### Build/test flow`, and `### Deployment/operations flow`; list absent evidence in section 14.
- In section 10 use `Change type`, `Suggested validation`, and `Evidence`.
- In section 11 record each item with `Decision`, `Status`, `Evidence`, `Trade-off`, and `Related ADR` when present.

For a monorepo, keep the document at the repository root, map only meaningful top-level components, describe inter-component boundaries, and state whether component-specific architecture documents are warranted. Do not create those files automatically.

Section 12 must tell agents to read this document before structural changes, preserve existing patterns and boundaries, keep changes scoped, update the architecture document when an intentional architectural change occurs, and report conflicts before editing. Keep these two baseline items: prefer existing repository patterns over new abstractions, and do not introduce new frameworks or cross-cutting refactors without explicit approval.

Section 13 must record the verification date, agent or tool, a summary of files inspected, commands considered or run, and confidence. Section 14 must make unresolved evidence gaps explicit rather than filling required sections with invented content. Verify claims against on-disk evidence before writing.

## Validation and Completion

Write no application code, infrastructure, tests, workflows, instructions, prompts, ADRs, or secondary analysis artifacts. Keep the document concise, normally 150-250 lines for a single-purpose repository and no more than 400 lines for a broad monorepo, with one H1, valid Markdown, a trailing newline, no unsupported claims, and no full repository tree. Use spaced table separators `| --- | --- |`; never `|---|---|`. Before writing, pressure-test overclaims, contradictions, invented flows, false monorepo unification, and unenforceable rules; downgrade unresolved claims to section 14.

Re-read the destination immediately before writing and stop on a concurrent change. Leave an already-correct document untouched. Run safe Markdown, link, and repository validators and distinguish commands actually executed from checks only considered. Report the changed path, architecture summary, material risks or unknowns, evidence inspected, and validation performed. Do not paste the full document unless requested.
