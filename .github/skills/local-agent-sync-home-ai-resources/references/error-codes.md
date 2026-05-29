# Error Codes

Use these stable error identifiers for planner, doctor, audit, and apply output.

| Code | Meaning | Default route |
| --- | --- | --- |
| `unknown-target` | The selected runtime target is not supported by the parser. | Stop and correct the target selection. |
| `unsupported-family` | The source resource family is not supported for the selected target. | Skip or block according to mode. |
| `docs-unverified` | Runtime support exists only as an unverified claim. | Allow `plan`, `audit`, and `doctor`; block `apply`. |
| `missing-target-root` | The runtime root directory does not exist. | Show remediation and block `apply` unless creation is approved. |
| `needs-directory-create` | The target directory tree can be created safely but does not exist yet. | Plan or doctor can suggest creation; `apply` needs explicit approval. |
| `permission-denied` | The runtime path exists but is not writable or readable enough for the selected mode. | Stop and surface the failing path. |
| `unsafe-home-path` | A resolved path escapes the expected home root or lands in an unsafe location. | Block immediately. |
| `symlink-not-allowed` | The resolved target path crosses a disallowed symlink boundary. | Block immediately. |
| `manifest-missing` | A manifest-backed mode needs state that does not exist yet. | Fall back to first-run planning or doctor guidance. |
| `manifest-corrupt` | The manifest exists but cannot be parsed or trusted. | Block apply and require remediation. |
| `target-exists-unmanaged` | A target path already exists but is not manifest-managed. | Block overwrite. |
| `target-modified-managed` | A manifest-managed target diverged from the last recorded content hash. | Block overwrite until reviewed. |
| `source-missing` | A catalog entry points to a source path that no longer exists. | Block that resource and flag catalog drift. |
| `source-invalid-skill` | A source skill bundle is incomplete for direct-copy sync. | Block that resource and fix the bundle. |
| `stale-managed` | A previously managed target is no longer planned. | Mark for prune, but do not delete automatically. |
| `prune-not-approved` | A stale managed resource could be removed, but prune was not approved. | Keep the file and report the follow-up. |
| `reverse-sync-blocked` | Source root is under home root, indicating attempted reverse sync (home → repo). | Block immediately. Sync must be repo → home only. |
