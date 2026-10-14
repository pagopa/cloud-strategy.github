# Knowledge Topology

Use this reference when the plan creates or changes the shape of a repository's documentation: which documents exist, where they live, and what each one must contain. [Knowledge scope](knowledge-scope.md) decides what may be touched; this reference decides what the touched documents are.

Load it in `setup`. Load it in `sync` only when the plan introduces an artifact that does not exist yet, such as the first document for a newly discovered component or domain.

## Contents

- [Supported layouts](#supported-layouts)
- [Strategic and tactical scope](#strategic-and-tactical-scope)
- [Layout migration](#layout-migration)
- [Evidence to artifact](#evidence-to-artifact)
- [Context documents](#context-documents)
- [Relationships](#relationships)
- [Domain levels](#domain-levels)
- [Cross-context home](#cross-context-home)
- [Rules document](#rules-document)
- [Documentation modes](#documentation-modes)
- [Anti-scope](#anti-scope)

## Strategic and tactical scope

Use the [knowledge types](knowledge-types.md) taxonomy to select a strategic
or tactical owner from repository evidence. The canonical README index maps
each evidenced type to its existing owner. Purpose belongs in its owner only
when it serves an unmet durable reader outcome. Do not create empty artifacts
or a separate memory file to complete a checklist.

A roadmap, backlog, proposal, or work outcome is not a knowledge type. Keep
those records with their existing owners. Record an accepted decision under
the appropriate ADR owner; do not infer acceptance, implementation, or outcome
from a proposal or a passing check.

README indexes inside the requested docs perimeter are ordinary targets.
Generated files remain with their generator. Canonical historical records,
including ADR status and decision history, and records required by local policy
stay with their existing owners. A date alone does not create a history
artifact. Treat generated files as protected evidence, not as authored
replacements.

## Claim classification

Classify each claim by what it means and who maintains it, not by whether it
contains a path, number, date, status, or command-like name. Use this primary
question:

> Does this sentence govern a domain or design decision, or describe operating machinery?

For a borderline claim, ask:

> Would it stay true if the component were rewritten with the same behavior?

Strategic claims establish purpose, direction, boundaries, decisions, domain
language, and rules. Tactical claims express durable UX language, naming
grammar, high-level policies, ownership boundaries, and stable contract names.
Operational claims describe how a particular implementation runs, including
flags, commands, exact expressions, byte or length caps, job wiring,
implementation inventories, procedures, volatile counts, dated observations,
and execution history.

| Tactical claim | Operational claim |
| --- | --- |
| A request moves through proposed, approved, implemented, and observed states. | Run `deploy --region <name>` from the release job. |
| The public API preserves the `authorization/v2` contract. | The handler applies this exact retry expression and a 30-second timeout. |

Put operational detail with the nearest maintained component owner, such as its
README or an authorized guide. When relocating it, consolidate duplicates
instead of appending every copy. If no maintained owner can usefully hold it,
propose removal; do not delete it without naming the exact path in the proposed
allowlist and obtaining approval. Preserve stable contracts, evidence paths,
approved-specification links, canonical ADR lifecycle/history, safety
constraints, and guides or records required by local policy. Knowledge
orientation explains durable intent and boundaries; it does not become an
execution backlog or completion ledger. Report discovered defects and conflicts
to the human, not in documents as warnings, disclaimers, invented unknowns, or
open questions.

## Supported layouts

Every repository has at least one knowledge domain. The evidenced domain count selects the layout; a declaration proposes a layout and never overrides the evidence.

Organize the top level by artifact type. Use L0-L3 only as navigation depth in
the plan: L0 is the repository index, L1 is repository orientation, L2 is the
owning domain or document type, and L3 is a specialist reference. These labels
do not require directories, metadata, or a fixed document at every level.
Group `reference/<area>/` when an area has about three or more reference
documents; with fewer, use flat `reference/<area>-<topic>.md` paths. The count
is a placement signal, not a quota.

Split a document only when it mixes reader modes or independent contracts or
consumers that materially change the reader path. A length near 250 lines is
a signal to inspect, not a split threshold. Do not split dated observations into
history artifacts automatically or split content solely by time validity.
Preserve canonical ADR status and decision history, plus records required by
local policy, with their existing owners.

| Domains evidenced | New default | Legacy layout |
| --- | --- | --- |
| One | Root `GLOSSARY.md` | Root `CONTEXT.md` |
| Two or more | Root `GLOSSARY-MAP.md` linking context `GLOSSARY.md` files | Root `CONTEXT-MAP.md` linking context `CONTEXT.md` files |

Preserve an existing canonical layout until migration is explicitly authorized.
A legacy layout is `legacy` drift: propose its format-only migration as a
separate wave.
For new context homes, prefer `docs/domain/<slug>/GLOSSARY.md`; preserve an
established code-colocated glossary when it represents the full context and
local ownership supports it. A component directory alone is not a domain.
Use `RULES.md` only for evidenced normative rules. Preserve established ADR
locations, including context-local directories; default new decisions to
`docs/adr/`. A changed domain set follows the ADR owner and acceptance authority.

Glossaries are lazy: create one only for a first meaningful resolved term at an
authorized destination. Optional absence is valid. First creation does not
itself require layout migration or a domain-set ADR.

## Layout migration

Use [legacy migration](legacy-migration.md) for detection, activation, transfer,
reference verification and interruption recovery. Changing an accepted domain
set requires a superseding decision. A format-only migration preserves that
set and its glossary, rules, and cross-context split. It needs no ADR unless an
accepted ADR names the legacy file names; then record a brief ADR that
supersedes only those names and cites the upstream convention. Never migrate
on re-derivation alone.

## Evidence to artifact

Create an artifact only when the listed evidence exists. Absence of evidence is a reported gap, never a placeholder document.

| Evidence | Artifact | Do not create when |
| --- | --- | --- |
| Durable purpose, scope, non-goals, stakeholders, or constraints with an unmet reader outcome | The existing Purpose owner mapped from the canonical index | An existing owner already covers the outcome or evidence is temporary or aspirational. |
| A significant component | A README in that component | The parent already documents it completely. |
| Terms whose meaning is repository-specific | The canonical glossary or legacy CONTEXT owner | The terms are general technology vocabulary. |
| Two or more areas with distinct vocabulary, state, or lifecycle | `docs/domain/<slug>/` per area | Only one area is evidenced; keep the vocabulary in its root owner. |
| A term whose meaning differs across two or more contexts, or a rule that spans two or more contexts | `docs/domain/cross-context/` (see [Cross-context home](#cross-context-home)) | Only one context is evidenced, or the term or rule belongs to one context. |
| Normative rules already stated in a validator, workflow, decision, or document | `docs/domain/<slug>/RULES.md` | No rule exists yet. Never invent a rule to fill the file. |
| A decision that is costly to reverse and surprising without context | An ADR | The decision is routine or already recorded. |
| A domain-set decision that meets the ADR admission criteria | An ADR recording the set and its evidence | The choice is routine, only a first glossary is created, or an accepted ADR records the same set. |
| Existing ADRs with no stated local format | `docs/adr/README.md` | The repository already states its ADR contract where the ADR author reads it. |
| Components, boundaries, and flows across the repository | `docs/architecture.md` | The repository has a single component fully covered by its README. |
| Relationships that cross the repository boundary | The relevant relationship sections of `docs/architecture.md` | No dependency leaves the repository. |
| An evidenced convention the repository follows by agreement | `docs/standards/<name>.md` | An existing owner already covers it, or no agreement is evidenced. Automation is enforcement evidence and does not change its category. |
| Recurring criteria that decide between alternatives | `docs/engineering-principles.md` | Only one occurrence is evidenced. |
| An evidenced chain from a declaration to its effect | `docs/guides/<name>.md` | A component README already covers the chain. |
| Durable project purpose, boundaries, and current orientation not already owned by an existing knowledge document | A project-orientation entry at the repository's existing canonical owner | The orientation is already complete, or the evidence is only temporary, aspirational, or inferred. |
| An approved specification that evidences one strategic or tactical type | A link from that type's existing owner | The source is draft, unapproved, temporary, or has no identifiable owner. |

Author guides with [standards maintenance](standards-maintenance.md). Use the
type-specific owner for Purpose and other strategic or tactical knowledge.

Every evidence-table row ends as one of four outcomes: `planned`, `existing owner covers`, `explicit exclusion`, or `considered, not evidenced`. The last outcome records that the reader outcome and detailed owner were considered but the evidence is insufficient; never create an artifact merely to satisfy a row. The plan accounts for every row. Standards, principles, and guides are the rows most often passed over, because nothing in the repository asks for them by name.

Before adding material, check whether an existing README, context document,
architecture document, ADR, or specification already owns it. Prefer a link
from the relevant type owner over a duplicate copy. If no canonical owner or
durable evidence exists, record the gap as `considered, not evidenced` and do
not create a placeholder.

## Context documents

A glossary contains definitions only. Use this shape for new and migrated
glossaries:

```markdown
# <Context name>

<One or two sentences on what this context is and why it exists.>

## Language

**<Term>**:
<One or two sentences defining what the term is.>
_Avoid_: <synonyms resolved as misleading>
```

Group terms under subheadings only when natural clusters emerge. Include only
repository-specific terms, not general technology vocabulary. Keep paths,
component and root names, rule identifiers, normative statements, and
relationships out of a glossary: rules go to `RULES.md`, component ownership
goes to `docs/architecture.md`, and relationships between contexts go to the
map.

A map has a title, `## Contexts` with one link and a one-line description per
context, and `## Relationships` with one bold `**A → B**` or `**A ↔ B**` entry
per evidenced relationship, naming the concept that crosses the boundary. It
holds no per-context component, declaration, or root sections; it may close
with one line pointing to `docs/architecture.md` for those. Reuse canonical
terms in authored knowledge and avoid resolved misleading synonyms. Flag
conflicts with accepted ADRs instead of silently redefining either source.

Existing `CONTEXT.md` and `CONTEXT-MAP.md` keep their local contract until an
approved migration. Do not rename a legacy mixed-content owner without first
moving its non-glossary content to the owners above; use the extraction
procedure in [legacy migration](legacy-migration.md).

When available, use `/mattpocock-domain-modeling` for vocabulary resolution;
local ownership, authority and accepted ADR contracts remain controlling.
When unavailable, state that fallback in the plan and use the self-contained
shapes above. Cite source paths for evidenced terms in the plan and report,
not inside definitions. Check source evidence,
meaning, examples and ambiguous synonyms. Report unresolved source conflicts
in chat instead of inventing definitions or precedence.

| Content | Owner |
| --- | --- |
| Resolved domain definitions | Canonical glossary or legacy context document |
| Component paths and responsibilities | Relevant architecture view |
| Reading order for a human | Root `README.md` |
| Reading order for an agent | Existing domain documentation guide |
| Decisions index and history | Existing ADR owner |
| Rules and invariants | Existing rules owner or `docs/domain/<slug>/RULES.md` |

## Relationships

Relationships are recorded at two levels, and the same pair is never described at both.

| Level | Where | What it records |
| --- | --- | --- |
| Between domains | The `## Relationships` section of the glossary map or legacy context map | The concept that crosses the boundary and the direction it travels |
| Between components, and toward systems outside the repository | The relevant relationship sections of `docs/architecture.md` | The dependency, its status, and its evidence path |

With a single domain there is no domain-to-domain relationship. The boundary the repository actually has is the one toward the outside, and it belongs to `docs/architecture.md`.

Describe each relationship as it is today, not as it should become. Use a named integration pattern only when the repository has already decided and recorded it; never infer a pattern from code shape. When no relationship is evidenced, record `none evidenced` and stop: an invented relationship is worse than an acknowledged absence.

In `docs/architecture.md`, keep the direction vocabulary neutral: `upstream`, `downstream`, `mutually dependent`, or `free`.

## Domain levels

Distinguish three levels and never collapse them:

1. **Knowledge domain** — a durable area of responsibility with its own vocabulary.
2. **Bounded context** — a knowledge domain that additionally owns state, lifecycle, and invariants, evidenced on disk.
3. **Component** — a physical unit of code or configuration.

Promote an area to its own domain only when an evidenced semantic or ownership boundary exists. The boundary must be visible in at least one of these forms: distinct ubiquitous language; an evidenced bounded context that owns its own lifecycle or invariants; or decoupled team ownership with responsibility that does not follow the neighbouring context. A different tool, state file, schema, delivery process, or deployability may corroborate a boundary, but an operational difference alone never creates one.

Enumerate that list explicitly: record a verdict and an evidence path for each candidate signal, then record the semantic or ownership boundary in the plan before the layout is selected. The enumeration precedes the ADR that records the domain set: a decision written from an impression rather than from the evidenced boundary is the ordinary way a repository acquires a layout it has to supersede in the next invocation. The plan promotes the area, or it carries the user's explicit decision to keep the narrower layout as the ledger reason. Relative size is not a signal: an area holding far less material than its neighbour is still a domain when its own semantic or ownership boundary holds. When an accepted ADR records a domain set the current evidence exceeds, report the drift and propose the superseding decision.

Name domains in the vocabulary the repository already uses. A domain name that appears nowhere in the repository is a sign the boundary is invented.

A domain needs no directory of its own. When its evidence is spread across configuration, validators, and reports that share one vocabulary, the boundary is still real; record the evidence paths instead of forcing a home for it.

## Cross-context home

Use `docs/domain/cross-context/` only when evidence shows a term whose meaning
differs across two or more contexts, or a normative rule that spans two or more
contexts. Its `GLOSSARY.md` resolves the shared or ambiguous terms; its
`RULES.md` holds cross-context rules that name the participating contexts.
List it in the map as a context. It is not a domain and does not count in the
domain-set ADR. A term or rule owned by one context stays in that context.

## Rules document

Write this document only when normative rules already exist somewhere in the repository. Each rule keeps a stable identifier and a fixed body.

In `sync` and `setup`, give every context one `RULES.md` outcome: existing,
planned with evidence, or `considered, not evidenced` naming the sources
inspected. Check security baselines, validators, workflows, decisions, and
contribution guides before concluding that no rule exists.

```markdown
# <Name> Rules

<One line stating who owns these rules.>

## <RULE-ID> — <short title>

- Rule ID: <RULE-ID>
- Serves: <PUR, PRI-nn, DIR-nn, or a strategic ADR>
- Owner: <owning context>
- Severity: <blocking | warning>
- Enforcement owner: <where the rule is checked, or `not enforced`>
- Evidence: <paths that show the rule exists>
- Remediation: <what to do when the rule is violated>
- Rule: <the normative statement>
```

Never derive a rule from prose that only describes a habit. If enforcement does not exist, record `not enforced` rather than implying a check.

When the repository already has a rules contract, keep its field names and
severity scale and add only `Serves`, as [alignment](alignment.md) defines it.

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
