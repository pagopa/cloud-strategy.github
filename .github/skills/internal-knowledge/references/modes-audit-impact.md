# Audit and Impact Modes

Both modes are strictly report-only and support `--format text` or `--format json`.

## Audit

Run `python3 scripts/knowledge.py audit --repo-root <path> --format json`. Pass optional `--config <path>` when the host supplies discovery policy.

The report covers documentation roots, the knowledge map, ADR identity and required sections, duplicate accepted ADR numbers, tracked README coverage, and presence or absence of host-configured CI assets. ADR audit inspects only `NNNN-<slug>.md` files and skips `docs/adr/README.md` as an index rather than an ADR body. Findings do not change the exit code because audit is evidence collection, not a write or enforcement operation. Invalid explicit config returns exit code `2`. Route CI-asset interpretation to [CI assets](ci-assets.md).

## Impact

Run `python3 scripts/knowledge.py impact --target <path> --repo-root <path> --format json`. Repeat `--target` to inspect multiple paths.

The report maps each target to tracked text files that reference it. Binary and unreadable files are skipped. The mode never renames, deletes, or rewrites references.
