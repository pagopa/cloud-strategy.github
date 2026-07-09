---
name: local-agent-sync-external-resources
description: Audit, plan, or apply declared external resource refreshes through the staged sync CLI.
---

# Local Agent Sync External Resources

## Contract

This skill owns the manifest-driven CLI that stages, validates, and applies
declared external resource refreshes safely. The single public entrypoint is
`scripts/sync_external_resources.py`.

## Modes

- `audit`: parse all registries, validate local paths, canonical names, hashes,
  watchlist shape, and dirty state. Does not fetch or write.
- `plan`: require an external workspace, build and validate the complete
  candidate, then emit the changed-path summary without repository writes.
- `apply`: perform `plan`, reject dirty targets unless `--allow-dirty`,
  generate one patch, run `git apply --check`, apply once, rebuild inventory,
  and rerun scoped validation.

## Safety

- Workspace must be outside the repository.
- Dirty managed targets block `apply` unless `--allow-dirty` is supplied.
- Override replay is atomic: if any override fails verification, no candidate
  changes reach the repository.
- Do not modify repository targets until the complete candidate tree,
  normalizations, overrides, and generated patch pass validation.

## Workflow

1. Run `audit` to validate the manifest, overrides, and local dirty-state without blocking on a dirty managed target.
2. Prepare source checkouts explicitly under the chosen source root.
3. Run `plan` with `--workspace` and, when needed, `--source-root` to confirm the candidate can be built.
4. Review the changed-path summary and override replay results.
5. Run `apply` only after `plan` succeeds; `apply` does not fetch sources implicitly.

If `plan` or `apply` reports `Missing upstream paths`, the message will name the expected root such as `/private/tmp/.../sources`. Populate that root first or pass an explicit `--source-root`.

## Canonical Commands

```bash
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py audit
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py plan --workspace /private/tmp/cloud-strategy-github-external-refresh
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py apply --workspace /private/tmp/cloud-strategy-github-external-refresh
```

## Override Rules

- Every approved imported in-place override must be registered in
  `references/imported-asset-overrides.yaml` with a replay patch and expected
  content hash.
- Replay uses clean `git apply --check` first, then `--3way --check` only when
  declared.
- Stop for review if neither path applies cleanly.

## Validation

- `python3 -m compileall .github/skills/local-agent-sync-external-resources/scripts`
- `python3 -m pytest -q tests/github/skills/local-agent-sync-external-resources/scripts`
- `python3 .github/scripts/validate_internal_skills.py --skill local-agent-sync-external-resources --strict`
- `make inventory-build`
- `make token-risks`

## Output

Report: mode, workspace, managed count, changed paths, override results,
validation, and blockers.

## Anti-Scope

- Do not refresh or modify any imported skill while implementing sync tooling.
- Do not add a plugin system, concurrency, compatibility aliases, legacy
  fallback paths, or a generic sync framework.
- Do not perform a live network refresh unless the user separately authorizes it.
