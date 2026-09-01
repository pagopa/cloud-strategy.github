# Knowledge Topology

Use this reference when the plan creates or changes the shape of a repository's documentation: which documents exist, where they live, and what each one must contain. [Knowledge scope](knowledge-scope.md) decides what may be touched; this reference decides what the touched documents are.

Load it in `setup`. Load it in `sync` only when the plan introduces an artifact that does not exist yet, such as the first document for a newly discovered component or domain.

## Contents

- [Supported layouts](#supported-layouts)
- [Layout migration](#layout-migration)
- [Evidence to artifact](#evidence-to-artifact)
- [Context documents](#context-documents)
- [Relationships](#relationships)
- [Domain levels](#domain-levels)
- [Rules document](#rules-document)
- [Documentation modes](#documentation-modes)
- [Anti-scope](#anti-scope)

## Supported layouts

Every repository has at least one knowledge domain. The evidenced domain count selects the layout; a declaration proposes a layout and never overrides the evidence.

| Domains evidenced | Root document | Domain documents |
| --- | --- | --- |
| One | Root `CONTEXT.md` | `docs/domain/<slug>/RULES.md` when normative rules exist |
| Two or more | Root `CONTEXT-MAP.md` | `docs/domain/<slug>/CONTEXT.md`, plus `RULES.md` when normative rules exist |

Domain documents always live under `docs/domain/<slug>/`. Never co-locate them with the code of a directory: a domain may span several directories or own none at all, and a path that holds only part of a domain misrepresents the boundary.

Both layouts keep decisions under `docs/adr/`, the system view in `docs/architecture.md`, and the domain set recorded as an ADR.

## Layout migration

When the approved plan moves a repository from one layout to the other, the migration is one coherent unit:

1. Record the new domain set as an ADR, with the evidence that selected it.
2. Create the new root document with the content the old one carried.
3. Update the layout declaration so it names the new root document and that ADR.
4. Update every reference to the previous root document.
5. Remove the previous root document only when the plan says so and nothing still points at it.

Never publish a layout change that leaves a declaration, a reading order, or a link pointing at a document that does not exist. If the wave limit prevents completing all five steps, do not start the migration in this invocation.

Once an accepted ADR records the domain set, the layout changes only through a superseding decision. Re-derivation may report that the evidence has moved; it never migrates the layout on its own.

## Evidence to artifact

Create an artifact only when the listed evidence exists. Absence of evidence is a reported gap, never a placeholder document.

| Evidence | Artifact | Do not create when |
| --- | --- | --- |
| A significant component | A README in that component | The parent already documents it completely. |
| Terms whose meaning is repository-specific | The root `CONTEXT.md`, or `docs/domain/<slug>/CONTEXT.md` when two or more domains are evidenced | The terms are general technology vocabulary. |
| Two or more areas with distinct vocabulary, state, or lifecycle | `docs/domain/<slug>/` per area | Only one area is evidenced; keep the vocabulary in the root document. |
| Normative rules already stated in a validator, workflow, decision, or document | `docs/domain/<slug>/RULES.md` | No rule exists yet. Never invent a rule to fill the file. |
| A decision that is costly to reverse and surprising without context | An ADR | The decision is routine or already recorded. |
| The domain set that selects the layout | An ADR recording it with its evidence | An accepted ADR already records the same set. |
| Existing ADRs with no stated local format | `docs/adr/README.md` | The repository already states its ADR contract where the ADR author reads it. |
| Components, boundaries, and flows across the repository | `docs/architecture.md` | The repository has a single component fully covered by its README. |
| Relationships that cross the repository boundary | Sections 6 and 7 of `docs/architecture.md` | No dependency leaves the repository. |
| A convention repeated across the repository with no automated check | `docs/standards/<name>.md` | The convention is already enforced; enforcement makes it a rule, not a standard. |
| Recurring criteria that decide between alternatives | `docs/engineering-principles.md` | Only one occurrence is evidenced. |
| An evidenced chain from a declaration to its effect | `docs/guides/<name>.md` | A component README already covers the chain. |

Author the last three artifacts with [standards maintenance](standards-maintenance.md).

The plan accounts for every row. Standards, principles, and guides are the rows most often passed over, because nothing in the repository asks for them by name.

## Context documents

`CONTEXT.md` and `CONTEXT-MAP.md` belong to the external context format. Draft them with `/mattpocock-domain-modeling` and follow that format exactly.

Never add a section the external format does not define, and never relocate one it does. A context document is a glossary; content that does not fit it belongs to another artifact:

| Content | Owner |
| --- | --- |
| Component paths and responsibilities | Section 5 of `docs/architecture.md` |
| Reading order for a human | The root `README.md` |
| Reading order for an agent | `docs/agents/domain.md` |
| Decisions index | `docs/adr/README.md` |
| Rules and invariants | `docs/domain/<slug>/RULES.md` |

When the external skill is unavailable, author the artifacts this skill owns, report the vocabulary layer as a gap, and state the unavailability in the plan before approval. Never substitute a local format for the missing one.

## Relationships

Relationships are recorded at two levels, and the same pair is never described at both.

| Level | Where | What it records |
| --- | --- | --- |
| Between domains | The relationships section of the context map | The concept that crosses the boundary and the direction it travels |
| Between components, and toward systems outside the repository | Sections 6 and 7 of `docs/architecture.md` | The dependency, its status, and its evidence path |

With a single domain there is no domain-to-domain relationship. The boundary the repository actually has is the one toward the outside, and it belongs to `docs/architecture.md`.

Describe each relationship as it is today, not as it should become. Use a named integration pattern only when the repository has already decided and recorded it; never infer a pattern from code shape. When no relationship is evidenced, record `none evidenced` and stop: an invented relationship is worse than an acknowledged absence.

In `docs/architecture.md`, keep the direction vocabulary neutral: `upstream`, `downstream`, `mutually dependent`, or `free`.

## Domain levels

Distinguish three levels and never collapse them:

1. **Knowledge domain** — a durable area of responsibility with its own vocabulary.
2. **Bounded context** — a knowledge domain that additionally owns state, lifecycle, and invariants, evidenced on disk.
3. **Component** — a physical unit of code or configuration.

Promote an area to its own domain only when at least two of these signals are evidenced: the same word means different things inside and outside it; it is represented differently from neighbouring areas; it serves a different audience; it uses a different tool set; it lives in a separate code base, state file, or schema; it follows a separate delivery process; it can be delivered independently; or another area depends on it directionally.

The list is closed, and two signals make promotion the default. Enumerate that list explicitly, with a verdict and an evidence path for each signal, and record the resulting count in the plan before the layout is selected. The enumeration precedes the ADR that records the domain set: a decision written from an impression rather than from the enumerated signals is the ordinary way a repository acquires a layout it has to supersede in the next invocation. The plan promotes the area, or it carries the user's explicit decision to keep the narrower layout as the ledger reason. Relative size is not a signal: an area holding far less material than its neighbour is still a domain when its own signals hold. When an accepted ADR records a domain set the current evidence exceeds, report the drift and propose the superseding decision.

Name domains in the vocabulary the repository already uses. A domain name that appears nowhere in the repository is a sign the boundary is invented.

A domain needs no directory of its own. When its evidence is spread across configuration, validators, and reports that share one vocabulary, the boundary is still real; record the evidence paths instead of forcing a home for it.

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
