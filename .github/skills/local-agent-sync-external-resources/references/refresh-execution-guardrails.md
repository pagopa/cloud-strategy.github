# Refresh Execution Guardrails

Use this reference before fetching or materializing upstream resources for
`local-sync-external-resources`.

## Workspace Rule

Stage upstream repositories outside the repository root. Use
`/private/tmp/cloud-strategy-github-external-refresh` by default for local runs.
Do not clone upstream repositories under repository-root `tmp/`.

Before graphify or completion reporting, run the bundled workspace guard and
resolve every blocking finding.

## Discovery Rule

Start from `references/managed-resource-scope.md`. Build a source-to-local map
for only the declared managed assets before running broad file listing,
repository-wide grep, or graph updates.

Use sparse or path-limited upstream retrieval when the upstream repository is
large. Fetch only managed skill directories and directly required sibling files.

## Validation Rule

Run imported override dry-run after refresh and before updating expected hashes.
Update expected hashes only after the patch is replayable or already applied.

Use scoped whitespace checks for local governance files and patch files. Do not
rewrite imported upstream content only to satisfy repository whitespace style.

## Reporting Rule

Completion reports must state:

- where upstream snapshots were staged
- whether the workspace guard passed
- whether graphify ran after repo-local refresh leftovers were absent
- which validators ran and which notices remained
