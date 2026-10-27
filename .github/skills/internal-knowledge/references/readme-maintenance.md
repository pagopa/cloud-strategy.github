# README Maintenance

Use this reference for authorized README knowledge updates: repository
orientation, the canonical knowledge index, and durable component purpose,
contracts, and boundaries. Component operation stays with its operational owner.

## Scope

README destinations may include:

- the root `README.md`, which orients readers to the repository;
- `docs/README.md`, which indexes strategic and tactical knowledge; and
- component READMEs whose durable knowledge is not already covered by a parent.

Use only destinations in the approved allowlist. Normalize and verify each
path before drafting. Discovery does not add component directories or other
README files to the allowlist. If an index is generated,
leave it with its generator and report the owner.

## Root README

Explain what the repository is for and where a reader should begin. Keep
implementation details with their maintained owners. Link to `docs/README.md`
when it exists or is an authorized target. Preserve the existing document
language, links, badges, and generated blocks.

## Canonical knowledge index

Maintain one canonical `docs/README.md` index. Map each evidenced knowledge
type to its existing owner and state **Load when** a reader needs that
knowledge. Use an explicit `not evidenced` entry for a type that has no
evidence; do not create an empty document to fill the gap.

In [complete setup](complete-setup.md), link prepared knowledge separately
with its placeholder status and link operational templates as reusable
support, not as active work or confirmed knowledge. Mock examples never
satisfy coverage.

The index publishes the alignment contract: operational work cites the
knowledge IDs it realizes; the skill reads operational artifacts only as
evidence; and `docs/` contains no reverse registry of operational work.
Link to [the alignment contract](alignment.md) for the detailed rules.

## Component README

Maintain evidence-backed purpose, responsibilities, stable contracts, and
ownership boundaries. Link to the maintained operational owner for usage,
commands, procedures, and validation instructions. Preserve existing operational
content and generated blocks; hand off operational changes to the component
owner. A new README needs only the knowledge and owner links supported by
evidence, not an operational template.

## Evidence and validation

Derive claims from repository-owned documents and other bounded evidence.
Distinguish observed facts from assumptions and report unresolved conflicts
instead of inventing a resolution. Keep one authoritative owner for each
contract and link to it rather than copying its detail.

Before writing, verify the authorized destination, its owner, local links,
generated blocks, and supported claims. Leave byte-equivalent content
unchanged. Run applicable Markdown and repository checks and report what each
check covered.
