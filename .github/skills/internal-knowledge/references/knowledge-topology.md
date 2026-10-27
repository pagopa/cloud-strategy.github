# Knowledge Topology

Use this reference when the plan creates or changes the shape of a repository's documentation: which documents exist, where they live, and what each one must contain. [Knowledge scope](knowledge-scope.md) decides what may be touched; this reference decides what the touched documents are.

Load it in `setup`. Load it in `sync` only when the plan introduces an artifact that does not exist yet, such as the first document for an approved Topic or component.

## Contents

- [Supported layouts](#supported-layouts)
- [Strategic and tactical scope](#strategic-and-tactical-scope)
- [Layout migration](#layout-migration)
- [Evidence to artifact](#evidence-to-artifact)
- [Context documents](#context-documents)
- [Relationships](#relationships)
- [Areas and Topics](#areas-and-topics)
- [Shared Terms](#shared-terms)
- [Rules document](#rules-document)
- [Documentation modes](#documentation-modes)
- [Anti-scope](#anti-scope)

## Strategic and tactical scope

Use the [knowledge types](knowledge-types.md) taxonomy to select a strategic
or tactical owner from repository evidence. The canonical README index maps
each evidenced type to its existing owner. Purpose belongs in its owner only
when it serves an unmet durable reader outcome. Do not create empty artifacts
or a separate memory file to complete a checklist.

For explicit whole-workspace installation, [complete setup](complete-setup.md)
permits marked scaffolds and operational documentation without inventing
knowledge claims. A prepared owner is not evidence of populated knowledge.

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

> Does this sentence govern an Area, Topic, or design decision, or describe operating machinery?

For a borderline claim, ask:

> Would it stay true if the component were rewritten with the same behavior?

Strategic claims establish purpose, direction, boundaries, decisions, Topic
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

Put operational detail in the Area's declared operational home: `work/<area>/`
for a document-only workspace, or the existing code paths for a code repository.
Never use `docs/` as a fallback operational home. When relocating it, consolidate duplicates
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

Use one DDD-inspired layout with plain vocabulary from
[knowledge types](knowledge-types.md#plain-vocabulary). Areas express purpose
and ownership; Topics own language and Rules. Directory counts do not prove
semantic boundaries. New Areas and Topics require human approval.

Organize the top level by artifact type. Use L0-L3 only as navigation depth in
the plan: L0 is the repository index, L1 is repository orientation, L2 is the
owning Area or document type, and L3 is a specialist reference. These labels
do not require directories, metadata, or a fixed document at every level.
Use the Area and Topic paths below rather than a second folder hierarchy.

Split a document only when it mixes reader modes or independent contracts or
consumers that materially change the reader path. A length near 250 lines is
a signal to inspect, not a split threshold. Do not split dated observations into
history artifacts automatically or split content solely by time validity.
Preserve canonical ADR status and decision history, plus records required by
local policy, with their existing owners.

| Condition | New default | Legacy layout |
| --- | --- | --- |
| One or more declared Areas | `docs/areas/<area>/README.md`, even for one Area | `docs/domains/<slug>/` or mixed project folders |
| One or more Topics | Topic-local `GLOSSARY.md` and root `GLOSSARY-MAP.md`, even for one Topic | Root `GLOSSARY.md`, `CONTEXT.md`, or `CONTEXT-MAP.md` |
| No declared Areas | Root `GLOSSARY.md` may remain | Root `CONTEXT.md` |
| An Area with zero Topics | No Area glossary | A project-wide glossary with no resolved owner |

```text
GLOSSARY-MAP.md                     # required as soon as one Topic exists
docs/
  README.md                        # strategic and tactical knowledge index
  adr/                             # ALL ADRs; new records carry Area:
  agents/                          # managed agent placement and promotion guides
  views/                           # optional Obsidian .base navigation indexes
  areas/
    _shared/                       # Shared Terms, created on first real case
    <area>/README.md                # Purpose, scope, boundary, Topics, decisions
    <area>/<topic>/GLOSSARY.md
    <area>/<topic>/RULES.md          # only when evidenced
work/<area>/                       # document-only operational home
  README.md
  sources/                         # append-only external inputs
  research/
  <deliverables>
tracker/<feature-slug>/             # operational work records
tracker/_templates/                # reusable spec and issue templates
tmp/                               # disposable, never durable evidence
```

`docs/` holds strategic and tactical knowledge, not analyses, data, scripts,
vendor offers, research, sources, or execution records. Managed guides and
optional views are navigation support, not accepted knowledge. Existing
evidence-backed knowledge owners such as `docs/project.md` remain valid.

In document-only workspaces, the operational root defaults to `work/` and may
be overridden in `AGENTS.local.md`. Mirror each `docs/areas/<area>/` with exactly
one `<operational-root>/<area>/` and vice versa. `_`-prefixed names are reserved
and never mirrored. In code repositories, the Area README instead declares
`Operational home:` with a list of existing code paths. Do not move code or
require a `work/` mirror. The skill writes only the Area README scaffold in
`work/`; it never authors operational deliverables or research.

Area READMEs list Purpose, scope, boundary, Topics with their
Core/Supporting/Commodity classification, operational home, and links to
decisions in `docs/adr/`. Topics, not Areas, receive that classification.
When the optional viewer is enabled, Area status is authoritative on the
docs side; the work README mirrors it. See [Obsidian vault](obsidian-vault.md).

Preserve an existing canonical layout until migration is explicitly authorized.
A legacy layout is `legacy` drift: propose its format-only migration as a
separate wave.
For new Topics use `docs/areas/<area>/<topic>/GLOSSARY.md`. Use `RULES.md` only
for evidenced normative rules. All ADRs belong in `docs/adr/`; never create an
Area-local ADR directory. Existing accepted ADR bodies remain unchanged.
Legacy ADR locations need an approved migration, not an automatic move.
An Area or Topic boundary change follows the ADR owner and acceptance authority.

Do not invent Topics to prepare a glossary. As soon as one Topic is approved,
create its glossary (a marked placeholder if no terms have resolved) and the
root map in the same approved wave. An Area has no glossary of its own.
Root `GLOSSARY.md` remains only in repositories without declared Areas.
Removing a Topic needs user approval and archives it; never delete it.

## Layout migration

Use [legacy migration](legacy-migration.md) for detection, activation, transfer,
reference verification and interruption recovery. Changing an accepted Area/Topic
set requires a superseding decision. A format-only migration preserves that
set and its glossary, Rules, and shared-language split. It needs no ADR unless an
accepted ADR names the legacy file names; then record a brief ADR that
supersedes only those names and cites the upstream convention. Never migrate
on re-derivation alone.

## Evidence to artifact

For ordinary knowledge maintenance, create an artifact only when the listed
evidence exists. Complete setup may prepare marked scaffolds under its
separate contract; absent content never permits invented claims.

| Evidence | Artifact | Do not create when |
| --- | --- | --- |
| Durable purpose, scope, non-goals, stakeholders, or constraints with an unmet reader outcome | The existing Purpose owner mapped from the canonical index | An existing owner already covers the outcome or evidence is temporary or aspirational. |
| A significant component | A README in that component | The parent already documents it completely. |
| Terms whose meaning is repository-specific | The canonical glossary or legacy CONTEXT owner | The terms are general technology vocabulary. |
| An approved Area with durable purpose and ownership | `docs/areas/<area>/README.md` and its declared operational home | Only a technical folder or speculative boundary exists. |
| An approved Topic with distinct meaning, state, or lifecycle | `docs/areas/<area>/<topic>/GLOSSARY.md` plus root `GLOSSARY-MAP.md` | No semantic or ownership boundary is evidenced. |
| Identical terms or Rules jointly used across Topics | `docs/areas/_shared/` (see [Shared Terms](#shared-terms)) | Meanings differ; keep separate definitions in their Topics. |
| Normative rules already stated in a validator, workflow, decision, or document | `docs/areas/<area>/<topic>/RULES.md` | No rule exists yet. Never invent a rule to fill the file. |
| A decision that is costly to reverse and surprising without context | An ADR | The decision is routine or already recorded. |
| An Area/Topic boundary decision that meets the ADR admission criteria | An ADR recording the set and its evidence | The choice is routine, only a first glossary is created, or an accepted ADR records the same set. |
| Existing ADRs with no stated local format | `docs/adr/README.md` | The repository already states its ADR contract where the ADR author reads it. |
| Components, boundaries, and flows across the repository | `docs/architecture.md` | The repository has a single component fully covered by its README. |
| Relationships that cross the repository boundary | The relevant relationship sections of `docs/architecture.md` | No dependency leaves the repository. |
| An evidenced convention the repository follows by agreement | `docs/standards/<name>.md` | An existing owner already covers it, or no agreement is evidenced. Automation is enforcement evidence and does not change its category. |
| Recurring criteria that decide between alternatives | `docs/engineering-principles.md` | Only one occurrence is evidenced. |
| An evidenced durable explanation of design intent or boundaries | `docs/guides/<name>.md` | An existing owner covers it, or it is an operational procedure rather than knowledge. |
| Durable project purpose, boundaries, and current orientation not already owned by an existing knowledge document | A project-orientation entry at the repository's existing canonical owner | The orientation is already complete, or the evidence is only temporary, aspirational, or inferred. |
| An approved specification that evidences one strategic or tactical type | A link from that type's existing owner | The source is draft, unapproved, temporary, or has no identifiable owner. |

Author guides with [standards maintenance](standards-maintenance.md). Use the
type-specific owner for Purpose and other strategic or tactical knowledge.

Every evidence-table row ends as one of four outcomes: `planned`, `existing owner covers`, `explicit exclusion`, or `considered, not evidenced`. The last outcome records that the reader outcome and detailed owner were considered but the evidence is insufficient; never create an artifact merely to satisfy a row. The plan accounts for every row. Standards, principles, and guides are the rows most often passed over, because nothing in the repository asks for them by name.

Before adding material, check whether an existing README, context document,
architecture document, ADR, or specification already owns it. Prefer a link
from the relevant type owner over a duplicate copy. If no canonical owner or
durable evidence exists, record the gap as `considered, not evidenced` and do
not create a placeholder outside the complete-setup exception.

## Context documents

A glossary contains definitions only. Use this shape for new and migrated
glossaries:

For an unpopulated complete-setup glossary, use only the orientation, marked
placeholder notice, and empty `## Language` section until definitions resolve.

```markdown
# <Topic name> Glossary

<One or two sentences on what this Topic is and why it exists.>

## Language

**<Term>**:
<One or two sentences defining what the term is.>
_Avoid_: <synonyms resolved as misleading>
```

Group terms under subheadings only when natural clusters emerge. Include only
repository-specific terms, not general technology vocabulary. Keep paths,
component and root names, rule identifiers, normative statements, and
relationships out of a glossary: rules go to `RULES.md`, component ownership
goes to `docs/architecture.md`, and relationships between Topics go to the
map.

A Glossary Map has a title, `## Topics` with one link and a one-line description
per Topic grouped by Area, an optional Shared Terms link, and
`## Relationships` with one bold `**A → B**` or `**A ↔ B**` entry
per evidenced relationship, naming the concept that crosses the boundary. It
holds no per-Topic component, declaration, or root sections; it may close
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
| Resolved Topic definitions | Canonical glossary or legacy context document |
| Component paths and responsibilities | Relevant architecture view |
| Reading order for a human | Root `README.md` |
| Reading order for an agent | Managed layout and vocabulary guides, or existing legacy guide |
| Decisions index and history | Existing ADR owner |
| Rules and invariants | Existing rules owner or `docs/areas/<area>/<topic>/RULES.md` |

## Relationships

Relationships are recorded at two levels, and the same pair is never described at both.

| Level | Where | What it records |
| --- | --- | --- |
| Between Topics | The `## Relationships` section of the Glossary Map or legacy context map | The concept that crosses the boundary and the direction it travels |
| Between components, and toward systems outside the repository | The relevant relationship sections of `docs/architecture.md` | The dependency, its status, and its evidence path |

With a single Topic there is no Topic-to-Topic relationship, but the root map
still exists. External system boundaries belong to `docs/architecture.md`.

Describe each relationship as it is today, not as it should become. Use a named integration pattern only when the repository has already decided and recorded it; never infer a pattern from code shape. When no relationship is evidenced, record `none evidenced` and stop: an invented relationship is worse than an acknowledged absence.

In `docs/architecture.md`, keep the direction vocabulary neutral: `upstream`, `downstream`, `mutually dependent`, or `free`.

## Areas and Topics

Distinguish three levels and never collapse them:

1. **Area** — a durable responsibility with a Purpose and ownership boundary.
2. **Topic** — a boundary within an Area where language and Rules have one meaning.
3. **Component** — a physical unit of code or configuration.

Propose an Area or Topic only when an evidenced semantic or ownership boundary
exists: distinct language, its own lifecycle or Rules, or independent ownership.
A different tool, state file, schema, delivery process, or deployability may
corroborate a boundary, but an operational difference alone never creates one.

Record a verdict and evidence path for each candidate signal before proposing
the Area/Topic set or its ADR. Relative size is not a boundary signal.
The plan records either the evidenced boundary or the user's explicit decision
to keep a narrower set. When evidence exceeds an accepted set, report drift
and propose the superseding decision; never create the boundary silently.

Name Areas and Topics in the repository's vocabulary. A name that appears
nowhere in the evidence is a sign the boundary is invented.

Evidence may be spread across configuration, validators, and reports. Record
those paths without moving them. An approved Area still has a docs-side README.

## Shared Terms

Create `docs/areas/_shared/` only on the first evidenced shared meaning or Rule.
Its `GLOSSARY.md` holds identical meanings shared across Topics; its `RULES.md`
names participating Topics and their shared obligations. List its glossary in
the map, but do not count `_shared` as an Area or Topic or mirror it in `work/`.
Same word with different meanings stays in separate Topic glossaries. Shared
Terms are a Shared Kernel only when joint ownership is explicitly declared;
see the closest DDD concepts in [knowledge types](knowledge-types.md#plain-vocabulary).

## Rules document

Write this document only when normative rules already exist somewhere in the repository. Each rule keeps a stable identifier and a fixed body.

In `sync` and `setup`, give every Topic one `RULES.md` outcome: existing,
planned with evidence, or `considered, not evidenced` naming the sources
inspected. Check security baselines, validators, workflows, decisions, and
contribution guides before concluding that no rule exists.

```markdown
# <Name> Rules

<One line stating who owns these rules.>

## <RULE-ID> — <short title>

- Rule ID: <RULE-ID>
- Serves: <PUR, PRI-nn, DIR-nn, or a strategic ADR>
- Owner: <owning Topic>
- Severity: <blocking | warning>
- Enforcement owner: <where the rule is checked and any exemptions the check skips, or `not enforced`>
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
