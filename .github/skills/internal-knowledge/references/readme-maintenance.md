# README Maintenance

Use this reference only for the repository-root README and the canonical
`docs/README.md` knowledge index. Component READMEs are outside the skill's
write scope; they belong to their component owners.

## Scope

The only README destinations are:

- the root `README.md`, which orients readers to the repository; and
- `docs/README.md`, which indexes strategic and tactical knowledge.

Use only destinations in the approved allowlist. Normalize and verify each
path before drafting. Do not widen the allowlist to component directories or
other README files discovered during the work. If an index is generated,
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

The index publishes the alignment contract: operational work cites the
knowledge IDs it realizes; the skill reads operational artifacts only as
evidence; and `docs/` contains no reverse registry of operational work.
Link to [the alignment contract](alignment.md) for the detailed rules.

## Evidence and validation

Derive claims from repository-owned documents and other bounded evidence.
Distinguish observed facts from assumptions and report unresolved conflicts
instead of inventing a resolution. Keep one authoritative owner for each
contract and link to it rather than copying its detail.

Before writing, verify the authorized destination, its owner, local links,
generated blocks, and supported claims. Leave byte-equivalent content
unchanged. Run applicable Markdown and repository checks and report what each
check covered.
