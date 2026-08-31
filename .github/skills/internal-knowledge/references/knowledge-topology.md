# Knowledge Topology

Use this reference when the plan creates or changes the shape of a repository's documentation: which documents exist, where they live, and what each one must contain. [Knowledge scope](knowledge-scope.md) decides what may be touched; this reference decides what the touched documents are.

Load it in `bootstrap`. Load it in `refresh` only when the plan introduces an artifact that does not exist yet, such as the first document for a newly discovered component or domain.

## Contents

- [Supported layouts](#supported-layouts)
- [Layout migration](#layout-migration)
- [Evidence to artifact](#evidence-to-artifact)
- [Root document contract](#root-document-contract)
- [Points of contact](#points-of-contact)
- [Domain levels](#domain-levels)
- [Context document](#context-document)
- [Rules document](#rules-document)
- [Documentation modes](#documentation-modes)
- [Anti-scope](#anti-scope)

## Supported layouts

Two layouts are supported. The repository declares which one applies; this reference never picks one on the repository's behalf.

| Layout | Root document | Domain documents | Use when |
| --- | --- | --- | --- |
| Single context | Root `CONTEXT.md` | None | One vocabulary covers the whole repository and no internal boundary changes the meaning of a term. |
| Multi context | Root `CONTEXT-MAP.md` | `docs/domain/<slug>/CONTEXT.md`, optionally `RULES.md` | Two or more areas own distinct vocabularies, state, or lifecycles. |

Both layouts keep decisions under `docs/adr/` and the system view in `docs/architecture.md`.

## Layout migration

When the approved plan moves a repository from one layout to the other, the migration is one coherent unit:

1. Create the new root document with the content the old one carried.
2. Update the layout declaration so it names the new root document.
3. Update every reference to the previous root document.
4. Remove the previous root document only when the plan says so and nothing still points at it.

Never publish a layout change that leaves a declaration, a reading order, or a link pointing at a document that does not exist. If the wave limit prevents completing all four steps, do not start the migration in this invocation.

## Evidence to artifact

Create an artifact only when the listed evidence exists. Absence of evidence is a reported gap, never a placeholder document.

| Evidence | Artifact | Do not create when |
| --- | --- | --- |
| A significant component | A README in that component | The parent already documents it completely. |
| Terms whose meaning is repository-specific | The root document's vocabulary section, or a context document | The terms are general technology vocabulary. |
| Two or more areas with distinct vocabulary, state, or lifecycle | `docs/domain/<slug>/` per area | Only one area is evidenced; keep the vocabulary in the root document. |
| Normative rules already stated in a validator, workflow, decision, or document | `RULES.md` in the owning area | No rule exists yet. Never invent a rule to fill the file. |
| A decision that is costly to reverse and surprising without context | An ADR | The decision is routine or already recorded. |
| Components, boundaries, and flows across the repository | `docs/architecture.md` | The repository has a single component fully covered by its README. |

## Root document contract

A single-context root `CONTEXT.md` contains, in order: purpose and boundary of the repository; the vocabulary as one term per subsection with its evidence path; the reading order; and a decisions index.

A multi-context root `CONTEXT-MAP.md` contains, in order:

1. **Context ownership** — one row per context with its glossary, its rules, its owner, and its boundary.
2. **Components** — one row per significant component with its path, its responsibility, the document that describes it, and its state boundary.
3. **Points of contact** — how the contexts meet, recorded as-is.
4. **Reading order** — the numbered path a new reader or agent follows.
5. **Decisions index** — the ADRs that constrain the map.

Omit a section only when it would be empty and say so in the report. Do not add sections that carry no evidenced content.

## Points of contact

A map that names contexts without describing how they meet is incomplete. Describe each contact as it is today, not as it should become.

Use only neutral relationship vocabulary: `upstream`, `downstream`, `mutually dependent`, or `free`. Name the concept that crosses the boundary and the direction it travels.

Use a named integration pattern only when the repository has already decided and recorded it. Never infer a pattern from code shape.

When no contact is evidenced, write `none evidenced` and stop. That is a valid, informative result; an invented relationship is not.

## Domain levels

Distinguish three levels and never collapse them:

1. **Knowledge domain** — a durable area of responsibility with its own vocabulary.
2. **Bounded context** — a knowledge domain that additionally owns state, lifecycle, and invariants, evidenced on disk.
3. **Component** — a physical unit of code or configuration.

Promote an area to its own domain only when at least two of these signals are evidenced: the same word means different things inside and outside it; it is represented differently from neighbouring areas; it serves a different audience; it uses a different tool set; it lives in a separate code base, state file, or schema; it follows a separate delivery process; it can be delivered independently; or another area depends on it directionally.

Name domains in the vocabulary the repository already uses. A domain name that appears nowhere in the repository is a sign the boundary is invented.

## Context document

```markdown
# <Name> Context

## Scope

<What this context owns and what it deliberately does not own.>

## Terms

### <Term>

<Definition in repository vocabulary, with the path that evidences it.>

## Relationships

- <Direction and concept exchanged with each neighbouring context.>
```

## Rules document

Write this document only when normative rules already exist somewhere in the repository. Each rule keeps a stable identifier and a fixed body.

```markdown
# <Name> Rules

<One line stating who owns these rules.>

## <RULE-ID> — <short title>

- Rule ID: <RULE-ID>
- Owner: <owning context>
- Severity: <blocking | warning>
- Enforcement owner: <where the rule is checked, or `not enforced`>
- Evidence: <paths that show the rule exists>
- Remediation: <what to do when the rule is violated>
- Rule: <the normative statement>
```

Never derive a rule from prose that only describes a habit. If enforcement does not exist, record `not enforced` rather than implying a check.

## Documentation modes

Classify the dominant mode of every planned document and record it in the plan. The classification guides drafting; it never becomes a directory, a metadata field, or a check.

| Reader need | Mode | Shape |
| --- | --- | --- |
| Learning by doing | Tutorial | A guided lesson with a guaranteed outcome. |
| Reaching a goal at work | How-to | Ordered steps stated from the reader's goal. |
| Looking something up | Reference | Neutral description that mirrors the machinery. |
| Understanding why | Explanation | Context, alternatives, and consequences. |

Review every draft against these failures before writing:

- two modes blended in one document, or all four collapsed into one;
- structure mirroring product features instead of reader needs;
- a how-to written from the machinery's perspective, or reduced to bare steps with no goal;
- explanation padding inside a how-to or a reference;
- instructions inside a reference, or a reference that no longer mirrors the machinery;
- an explanation that absorbs the other three modes;
- generated reference treated as sufficient documentation on its own.

The remedy for a mixed document is always to link, never to merge. Move the foreign material to the document that owns that mode and cross-reference it.

## Anti-scope

- Never create empty mode directories such as `tutorials/`, `how-to/`, `reference/`, or `explanation/`. A structure with nothing in it is worse than no structure.
- Never add a documentation-mode field to front matter, a manifest, or a schema.
- Never propose a check that enforces documentation modes.
- Never restructure documents the approved plan does not include. Report the defect and leave the file alone.
- Never rewrite a repository's documentation wholesale to reach a target shape. Improve it in ordered waves, each one publishable on its own.
