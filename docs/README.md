# Strategic and Tactical Knowledge Index

This index maps each evidenced knowledge type to its current owner. Read the
linked document for detail; this index does not override `AGENTS.md`, policy,
skills, validators, or other authoritative owners.

## Knowledge types

| Type | Owner | Load when |
| --- | --- | --- |
| Purpose (`PUR`) | [Repository context](repository-context.md) | Reviewing the repository's role, scope, stakeholders, or goals. |
| Principles (`PRI-nn`) | Not evidenced — no distinct cross-cycle Principles owner exists. | A stable repository principle needs to be applied. |
| Direction (`DIR-nn`, `RSK-nn`) | Not evidenced — no time-boxed direction owner or review horizon exists. | Reviewing strategic priorities or risks. |
| Language | [Catalog Governance context](domain/catalog-governance/CONTEXT.md); [Source Synchronization context](domain/source-synchronization/CONTEXT.md) | Interpreting catalog, synchronization, and ownership terms. |
| Strategic decisions (`ADR-nnnn`) | [ADR index](adr/README.md), especially [ADR-0002](adr/0002-knowledge-domain-layout.md) | Changing the repository's durable knowledge-domain layout. |
| Tactical decisions (`ADR-nnnn`) | [ADR index](adr/README.md), especially [ADR-0001](adr/0001-terraform-skill-routing-boundaries.md) | Changing Terraform skill routing or its implementation boundary. |
| Rules | [Catalog Governance rules](domain/catalog-governance/RULES.md); [Source Synchronization rules](domain/source-synchronization/RULES.md) | Changing catalog ownership, validation, or source-to-target preservation. |
| Standards (`STD-<area>-nn`) | Not evidenced — `tech.md` describes observed tooling but is not a shared standards owner. | Applying a repository-wide convention or naming grammar. |
| Structure | [Repository structure](structure.md); [Architecture](architecture.md) | Finding repository areas, boundaries, components, or flows. |

## Alignment contract

Operational work cites the knowledge IDs it realizes. The `internal-knowledge`
skill reads operational artifacts only as evidence. `docs/` contains no reverse
registry of operational work. See the [alignment contract](../.github/skills/internal-knowledge/references/alignment.md)
for IDs, `Serves:`, precedence, and audit outcomes.

## Other references

- [Technology and validation reference](tech.md) describes the observed stack
  and maintainer checks.
- [Source synchronization guide](guides/source-sync.md) describes an
  operational workflow; its detailed contracts remain with the owning skills.
