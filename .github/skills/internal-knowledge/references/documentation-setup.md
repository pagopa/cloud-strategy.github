# Documentation Setup

Use this reference when a repository has no documentation structure or when `audit` reports that the structure is incomplete.

## Create the Setup

1. Inspect the repository's existing README files, documentation, and local instructions before choosing names or locations.
2. Create `docs/` when the repository has durable guidance that does not belong in the root `README.md`.
3. Run `python3 scripts/knowledge.py bootstrap --repo-root <path> --format json` to generate `docs/knowledge-map.yaml` from tracked README and documentation files.
4. Add missing documentation requested by the user, following nearby repository conventions.
5. Register each new documentation path with `update --target <path>`.

The root `README.md` remains the entry point. Use `docs/` for detailed guidance and `docs/adr/` for architectural decisions when the repository uses ADRs. When `docs/adr/README.md` exists, it defines the local ADR format; otherwise use the bundled [minimal MADR reference](madr-minimal.md).

## Check the Setup

Run `audit` after creation or updates. Resolve findings for a missing `docs/` directory, a missing knowledge map, invalid or duplicate accepted ADRs, and unregistered component READMEs. A repository may use a smaller documentation layout when those optional structures are not needed.
