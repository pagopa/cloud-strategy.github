# Inventory And Check

This reference owns the generic host-config schema, report contracts, exit codes, and write boundaries for portable discovery. Host repositories supply `docs/knowledge-config.yaml`; this skill may read that file and must never write it.

## Host Config Schema

An explicitly supplied config is a mapping with exactly these fields and no component inventory:

- `scan_roots`: repository-relative roots to inspect
- `exclusions`: glob patterns that must never appear in reports
- `expected_assets`: host-configured CI asset paths keyed by a host-chosen name
- `canonical_documents`: host-owned canonical document paths
- `coverage_rules`: per-kind coverage requirements, each declaring exactly one `require` key whose only accepted value is `readme`

A rule with a missing `require`, an extra key, or any other `require` value is rejected at load time. Declaring a kind here is the only way to make its missing README a `check` failure; kinds absent from `coverage_rules` are inventoried but not gated.

Missing optional `--config` leaves portable empty defaults. Invalid or unreadable explicit config returns exit code `2`.

## Inventory

`inventory` is report-only. It writes nothing. It emits stable JSON with `mode`, `status`, `scope`, `components`, `relationships`, `capabilities`, `findings`, and evidence paths. Unsupported or ambiguous classification is a finding, not an invented class.

Supported component kinds:

- `terraform_root`
- `terraform_local_module`
- `github_composite_action`
- `github_workflow`
- `declaration_data`
- `script_wrapper`
- `test`
- `validator_tool`

Terraform capability summaries list provider resource and data-source types plus static counts by owner. They must not emit resource addresses or runtime-instance claims. Relationships cover local module sources, local workflow action uses, wrapper or caller references, and documentation references when evidenced. Excluded and untracked generated paths must never appear.

## Check

`check` is fail-closed deterministic conformance. It reuses the inventory model, writes nothing, and uses this exit-code contract:

- `0` when configured documents and coverage rules pass
- `1` when coverage or register agreement fails
- `2` when required configuration is missing or invalid

`check` verifies that each configured canonical document exists in `docs/knowledge-map.yaml` and is covered directly or by an ancestor in `docs/knowledge-components.txt`. It reports any discovered top-level canonical guide that lacks a config classification. README-component registration is a distinct check keyed only to discovered maintained README owners.

Semantic truth remains a human review. Do not treat wording quality as a machine gate.

## Write Boundary

`audit`, `impact`, `inventory`, `check`, and `update --all` never write files. `bootstrap` and `update --target` write only `docs/knowledge-map.yaml` and must leave host config byte-identical.
