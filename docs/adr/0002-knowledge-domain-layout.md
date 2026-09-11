# Knowledge domain layout

The repository uses a multi-context knowledge layout with `catalog-governance` and `source-synchronization` domains because the source catalog and the source-to-target synchronization system have distinct vocabularies, audiences, toolsets, and lifecycles. The layout is recorded in [CONTEXT-MAP.md](../../CONTEXT-MAP.md); the evidence is the source catalog and inventory under `.github/`, the synchronization contracts under `.github/skills/local-*`, and their separate contract-test and validation entrypoints.
