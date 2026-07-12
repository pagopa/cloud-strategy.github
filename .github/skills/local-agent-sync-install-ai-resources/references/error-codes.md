# Error Codes

Convert every active code into its plain-language route. Do not surface a bare
code in an operator report.

| Code | Meaning | Route |
| --- | --- | --- |
| `unknown-target` | The requested runtime target is unsupported. | Correct the target. |
| `unsupported-family` | The target does not support this resource family. | Select a supported target. |
| `docs-unverified` | Runtime support is not documented enough for writes. | Use read-only modes or add support evidence. |
| `needs-directory-create` | A required runtime directory is absent. | Rerun apply with explicit `--create-missing-dirs`. |
| `permission-denied` | The runtime path is not accessible enough. | Repair permissions. |
| `unsafe-home-path` | A path escaped its allowed runtime location. | Stop and repair the path. |
| `symlink-not-allowed` | The runtime root or an intermediate path crosses a link boundary. | Replace it with a real confined directory. |
| `symlink-unsupported` | The filesystem cannot create required skill links. | Use a supported filesystem; copied skills are not allowed. |
| `link-target-missing` | A managed home link is broken or its source disappeared. | Restore the source or remove the broken link after review. |
| `link-target-mismatch` | A home link points to another checkout. | Rerun after correcting the link; do not overwrite it automatically. |
| `manifest-missing` | A read-only manifest-backed mode has no prior state. | Treat it as first-run evidence. |
| `manifest-corrupt` | The manifest cannot be trusted. | Repair or remove the state before apply. |
| `target-exists-unmanaged` | A copied agent target is unmanaged. | Preserve it or resolve ownership before apply. |
| `target-modified-managed` | A copied agent changed after the recorded hash. | Review the local change before replacing it. |
| `source-missing` | A catalog source no longer exists. | Repair the catalog or source. |
| `source-invalid-skill` | A repository skill lacks `SKILL.md`. | Repair the source bundle. |
| `stale-managed` | A copied managed resource is no longer planned. | Review and use explicit `--prune-managed` if appropriate. |
| `prune-not-approved` | Copied-resource pruning needs explicit approval. | Rerun apply with `--prune-managed`. |
| `stale-content-drifted` | A stale copied resource changed locally. | Review it before deletion. |
| `stale-path-unresolvable` | A stale path cannot be confined safely. | Repair manifest state before deletion. |
| `reverse-sync-blocked` | The requested source is inside home sync state. | Select the repository source; reverse writes are forbidden. |
| `retire-target-overlap` | A runtime was selected and retired simultaneously. | Make target selection unambiguous. |
