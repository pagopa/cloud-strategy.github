# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The domain-modeling skill creates them lazily when terms or decisions actually get resolved.

## File structure

This repository uses the multi-context layout:

```text
/
├── CONTEXT-MAP.md
├── docs/adr/
│   ├── 0001-terraform-skill-routing-boundaries.md
│   └── 0002-knowledge-domain-layout.md
└── docs/domain/
    |-- catalog-governance/CONTEXT.md
    `-- source-synchronization/CONTEXT.md
```

## Use the glossary's vocabulary

When output names a domain concept, use the term defined in the relevant domain `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If a concept isn't present in the relevant glossary, reconsider whether the term belongs to the project or note the genuine documentation gap.

## Flag ADR conflicts

If output contradicts an existing ADR, surface the conflict explicitly rather than silently overriding it. Read the relevant domain glossary and `docs/adr/` records before structural changes.
