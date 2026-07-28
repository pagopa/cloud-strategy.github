# Sync Contract Reference

## Path Ownership

### Source-managed exact copy

These files are mirrored byte-exact from source to target:

- `AGENTS.md`
- `.python-version`
- `.pre-commit-config.yaml`
- `.editorconfig`
- `.github/copilot-instructions.md`
- `.github/workflows/_pre-commit.yml`

### Source-managed instructions

Source files under `.github/instructions/` are mirrored to the target. The planner discovers them recursively.

### Target-local instructions (preserved)

Any file under `.github/instructions/` whose filename starts with `local-` is preserved byte-identical. The planner never mutates these paths.

### Target-only non-local instructions (deleted on apply)

Any file under `.github/instructions/` that is not in the source and does not start with `local-` is planned for deletion during `apply`.

### AGENTS.local.md (create-once)

Created as a header-only seed from `templates/AGENTS.local.md` only when the target lacks the file. An existing target `AGENTS.local.md` is preserved byte-identical and never overwritten or deleted.

## Action Semantics

| Action | Meaning |
| --- | --- |
| `create` | File is missing in the target; will be written on apply. |
| `update` | File exists in the target but differs from source; will be overwritten on apply. |
| `delete` | Target-only non-local instruction; will be removed on apply. |
| `preserve` | File matches source or is consumer-owned; no mutation on apply. |

## Error Codes

| Code | Condition |
| --- | --- |
| `missing-plan` | Apply requested without a saved plan file. |
| `dirty-managed-overlap` | A dirty target path overlaps a planned managed mutation. |
| `stale-plan` | Saved plan fingerprint does not match the current plan. |
| `source-contract` | A required source file is missing or source and target resolve to the same directory. |

## Convergence

A target is converged when a fresh `plan` reports zero managed mutations (`managed_mutation_paths` is empty). After a converged apply, the target plan file is removed.
