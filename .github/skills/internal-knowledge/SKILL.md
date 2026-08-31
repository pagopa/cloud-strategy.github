---
name: internal-knowledge
description: Use when creating, aligning, or materially refreshing repository knowledge documents, including README files across a repository, the root context document, `docs/architecture.md`, domain context and rules documents, engineering standards, principles, and guides, and architectural decision records (ADRs).
---

# Internal Knowledge

Create durable repository documentation from bounded, on-disk evidence.

## When to use

- Asking what this skill would do before committing to it, with `/internal-knowledge help <goal>`.
- Aligning or bootstrapping a repository's knowledge documents when the declared layout is missing, incomplete, or contradicted by what exists on disk.
- Refreshing README files across a repository, including the missing README of a significant component.
- Creating or refreshing a root context document, `docs/architecture.md`, or a domain context and rules document.
- Recording an engineering standard, principle, or guide the repository already practises.
- Recording, revising, or superseding an architectural decision.

## When not to use

- Installing or changing a workflow, composite action, validator, documentation generator, or coverage manifest; this skill reports the enforcement gap instead of closing it.
- Fixing spelling, wording, or Markdown structure without a material documentation change; route those to `/internal-markdown`.
- Explaining the repository in chat without authoring a document.

## Workflow

1. Resolve one repository root, then resolve exactly one mode with [knowledge scope](references/knowledge-scope.md): `help` when the request opens with `help` or asks what this skill can do, `targeted` for explicit user destinations, `refresh` when the declared knowledge layout is already realized, `bootstrap` when that layout is absent, incomplete, or contradicted by the repository. `help` answers with the intent, the mode, the destinations at stake, and the prompt to run, then stops without writing.
2. In `refresh` and `bootstrap`, discover targets, derive the document set with [knowledge topology](references/knowledge-topology.md), and present the preflight plan for approval; approval is what authorizes the write allowlist. In `targeted`, skip the gate and use only the supplied destinations.
3. Read applicable repository instructions, existing target content, and only the evidence needed to support material claims.
4. Draft each authorized target with its authoring reference:
   - README files with [README maintenance](references/readme-maintenance.md);
   - `docs/architecture.md` with [architecture maintenance](references/architecture-maintenance.md);
   - decisions with [ADR maintenance](references/adr-maintenance.md);
   - standards, principles, and guides with [standards maintenance](references/standards-maintenance.md);
   - context documents with `/mattpocock-domain-modeling`, whose format this skill follows without adding to it.
5. Recheck each destination immediately before writing, apply the unchanged predicate, then write at most one wave.
6. Run applicable Markdown and repository validators. Report changed paths, evidence used, validation run, the exclusion ledger, the enforcement gap, and the next wave.

## Boundaries

- This skill authors documents. It never writes workflows, composite actions, validators, documentation generators, coverage manifests, or repository policy files, and never installs a check. Report the enforcement gap instead of closing it.
- `CONTEXT.md` and `CONTEXT-MAP.md` follow an external context format. Never add a section that format does not define; content that does not fit belongs to another artifact. When the external skill is unavailable, author the rest and report the vocabulary layer as a gap.
- A declaration states intent, not fact. Never let a declared layout override the domain set the repository evidences.
- The repository declares its own knowledge layout. Read that declaration; never substitute a central preference for it, and change it only inside an approved plan.
- `targeted` never widens into a repository-wide refresh. Report the wider gap instead of acting on it.
- Write only destinations the approved plan or the explicit request authorizes. Evidence discovered while drafting produces a reported gap, never an unplanned write.
- Preserve accepted ADR bodies; use the supersession flow for a changed accepted decision.
- Preserve existing generated blocks and repository-owned documentation markers byte-for-byte. Never introduce a new marker, profile mechanism, or coverage manifest.
- Never scaffold empty documentation-mode directories, never record a documentation mode as metadata, and never propose a check that enforces one.
- Route ordinary copy edits and Markdown structure fixes to `/internal-markdown`.
- Keep repository policy, application code, infrastructure, tests, and workflows outside the write scope.

## House Rules

- Treat the target repository's `docs/adr/README.md` as the authoritative ADR house format when present; use the bundled [minimal MADR reference](references/madr-minimal.md) only as a portable fallback.
- Store ADRs as `NNNN-<slug>.md` and keep at most one accepted ADR per number.
- Preserve the language of an existing document. Write new documents in English unless a local contract requires another language.
- When a repository serves a profile README from `.github/`, state which file is the displayed entry point and stop when the two entry points contradict each other.
