# Strategic and Tactical Knowledge Types

Use this reference to classify durable repository knowledge and select its
owner. The skill maintains strategic and tactical knowledge and their
alignment. Complete setup also prepares marked scaffolds and operational
documentation under [its separate contract](complete-setup.md); those
artifacts do not become strategic or tactical knowledge by existing.

## Strategic knowledge

| Type | What it records | Default home for a new repository |
| --- | --- | --- |
| Purpose | Scope, non-goals, stakeholders, and constraints | `docs/project.md` |
| Principles | Durable principles that apply across cycles | `docs/principles.md` |
| Direction | Diagnosis, guiding policy, objectives with a horizon, assumptions, and strategic risks | `docs/direction.md` |
| Language | Domain terms and their intended meanings | Root `GLOSSARY.md`, or context glossaries linked from `GLOSSARY-MAP.md`; legacy CONTEXT owners migrate when approved |
| Strategic decisions | Accepted choices that establish or change direction | `docs/adr/` |

## Tactical knowledge

| Type | What it records | Default home for a new repository |
| --- | --- | --- |
| Rules and policies | Normative requirements that govern work | `docs/domains/<context>/RULES.md` or a policy owner |
| Standards and conventions | Shared practices, including naming grammar | `docs/standards/` |
| Structure and boundaries | Components, domains, contracts between parts, and repository maps | `docs/architecture.md`; use `contracts/` only when needed |
| Tactical decisions | Accepted implementation or governance choices within direction | `docs/adr/` |

These nine types are optional. Create a file only when repository evidence
supports durable content for it. No file is created without evidence merely to
complete a type list. A new repository may use the default homes above; an
existing repository keeps its established files. Its `docs/README.md` maps
each evidenced type to its local owner, says when to load that owner, and
records each approved type exclusion with its reason.

In complete setup, distinguish `placeholder` owners from confirmed content.
A glossary scaffold is required preparation, not proof of resolved language.
Other scaffolds need an approved reader need rather than taxonomy completion.
Templates and mock examples never satisfy knowledge coverage.

Every type still receives an outcome in `sync` and `setup`, so an absence is a
visible decision rather than an omission. Purpose, Principles, and Direction
are human decisions. When repository evidence is insufficient for them,
propose candidate content in chat and ask the human. Content the human
explicitly accepts in the conversation is evidence: record the accepting role
and date in the owner body. Unaccepted proposals stay in chat.

An approved specification may be linked as evidence from the knowledge type
it supports. Keep the durable claim with that type's existing owner; do not
create a separate project-memory document. A draft or proposal is not an
accepted decision and does not become durable guidance by being useful.

## Maintenance behavior

Apply one behavior according to the type and its change lifecycle:

| Behavior | Use for |
| --- | --- |
| Update in place | Purpose, Principles, Language, Rules, Standards, and Structure |
| Supersede with a new record | Strategic and tactical decisions |
| Review within the stated horizon | Direction |
| Point to the source | Ownership, inventories, and work state that belong elsewhere |

Only Direction is time-boxed. State its horizon and the role responsible for
review in its body. After the horizon, describe it as **not reconfirmed**;
do not present it as current until reviewed. Principles hold across cycles.
The guiding policy applies to one cycle and cites the Principles it uses.

## Excluded content

Procedures, commands, operational inventories, component operation, work
state, and prose ownership are not strategic or tactical knowledge. Keep them
with their operational owner and point to that source when useful. Read
operational artifacts only as evidence for a proposed durable promotion; do
not copy their operational content into these knowledge documents.

`RSK` records strategic uncertainty about direction. A defect is not an RSK:
report defects to a human and do not write them into knowledge documents.

Preserve the language of an existing document. Write new documents in English
unless a local contract requires another language.
