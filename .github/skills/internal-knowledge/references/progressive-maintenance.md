# Progressive Knowledge Maintenance

Use this reference when durable knowledge is resolved during a conversation.
It changes update timing within an authoring mode, not mode or authority.
`help`, `audit`, and `align` remain read-only.

## Resolution and authority

Keep candidate definitions, disputed meanings, and tentative decisions in chat.
Do not create a placeholder or persist an unresolved candidate. A claim is ready
when its meaning is resolved with the user or authoritative evidence, its owner
and maturity are known, and it adds durable knowledge without contradiction.

Update the canonical authorized destination during the conversation once those
conditions hold. Do not wait until conversation close or ask again for approval
already granted to that content and path. Reread the destination before each
coherent update, preserve concurrent edits, and report the observed delta.
Unchanged content produces no write.

The allowlist may name an exact future path before it exists. Authority for one
glossary does not include a new context, map, index, declaration, or ADR. Keep
resolved content in chat when its destination is unauthorized; report the
concrete additional scope needed. Resolution never expands the allowlist.

## Maturity by owner

| Knowledge | Admission and maintenance |
| --- | --- |
| Language | Resolve meaning, boundary and examples; update the canonical glossary or legacy context owner. |
| Purpose and Structure | Update durable descriptions supported by current evidence. |
| Principles, Rules and Standards | Require the applicable normative authority; preference or repeated habit alone does not establish an obligation. |
| Direction | Preserve its horizon and review authority; expiry needs reconfirmation, not an inferred refresh. |
| Proposed ADR | Revise within its local proposal and review contract. |
| Accepted ADR | Preserve its decision body; a changed decision needs a superseding ADR and explicit acceptance authority. |

Use the detailed artifact owner before drafting. A resolved definition is not
proof that a design decision is accepted, implemented, or observed. Preserve
stable item IDs when moving accepted content; do not renumber or reuse them.

## Coherent updates

Allow successive coherent updates within the same invocation as knowledge
resolves. Each update must satisfy the artifact contract and keep required
links coherent within authorized scope. Link only to existing destinations.
Do not publish an index pointing to a future update.

Treat a layout migration as the complete unit in
[legacy migration](legacy-migration.md), not as independent glossary updates.
At interruption or close, report actual changes, pending candidates in chat,
scope gaps and validation coverage using [knowledge report](knowledge-report.md).
These are agent instructions; they do not provide a watcher, atomic edits or
runtime enforcement.
