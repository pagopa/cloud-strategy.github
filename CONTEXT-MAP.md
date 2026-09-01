# Context Map

The repository has two knowledge domains: catalog governance and source synchronization.

## Contexts

- [Catalog governance](./docs/domain/catalog-governance/CONTEXT.md) - owns the vocabulary for source-managed Copilot assets, catalog boundaries, and validation contracts.
- [Source synchronization](./docs/domain/source-synchronization/CONTEXT.md) - owns the vocabulary for materializing source assets into consumer repositories and home runtimes.

## Relationships

- **Catalog governance -> Source synchronization**: Source-owned resource classifications and eligibility declarations enter synchronization planning through the repository sync contract and home sync catalog. Evidence: `.github/skills/local-sync-repos/references/sync-contract.md`, `.github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml`.
