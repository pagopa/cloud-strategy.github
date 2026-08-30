# Update Modes and Approval Requirements

## Explicit Targets

Run `python3 scripts/knowledge.py update --target <path> --repo-root <path> --format json`. Repeat `--target` for every approved path.

The command validates repository-relative paths, rejects traversal and protected policy paths, preserves existing manifest paths, and writes only `docs/knowledge-map.yaml`. It does not edit the target documents.

## Repository Scan

Run `python3 scripts/knowledge.py update --all --repo-root <path> --format json`.

This command is report-only. It returns `approval-required` and a deterministic `resolved_targets` list. Review that list, then re-supply only approved entries through `--target`. Approval of `--all` itself never grants a write allowlist.

`AGENTS.md` and `AGENTS.local.md` remain report-only even when explicitly supplied; attempts return exit code 2 and status `blocked`.
