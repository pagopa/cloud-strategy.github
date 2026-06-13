# Agent OS Foundation Provenance

This folder is a bounded foundation snapshot for inspection only.

## Selected upstream snapshot

- Repository: `https://github.com/buildermethods/agent-os`
- Selected immutable commit: `cae8e664fb59a01869718c3151e0f45b7a06a2fb`
- Baseline comparison tag: `v3.0.0` (`809fb4e3e20451e3dd9ad9b253111776db373518`)
- License at selected baseline: MIT (`tmp/superpowers/adopt-agent-os/_evidence/LICENSE.baseline`)

## Why this snapshot

- Baseline v3.0.0 evidence showed known defects for this environment: missing `profiles/default/` and `tac` dependency in `scripts/project-install.sh`.
- Selected commit evidence shows `default_profile: default`, an existing `profiles/default/`, and no `tac` usage.
- A temporary sandbox installation test succeeded and created `agent-os/standards/index.yml` and `.claude/commands/agent-os/` as documented.

## Materialization boundary for this phase

Included in repository:

- `agent-os/standards/index.yml`
- `agent-os/provenance.md`

Excluded on purpose:

- `.claude/**`
- Runtime integration or slash-command activation
- Product/spec migration, canonical ownership changes, sync propagation, and Superpowers replacement

## Deterministic update policy

To update this foundation snapshot in future work:

1. Select an immutable upstream commit (never mutable `main`).
2. Record snapshot metadata and rationale in this file.
3. Run a sandbox install test and capture evidence under `tmp/superpowers/adopt-agent-os/_evidence/`.
4. Apply bounded diff review and run required validators before claiming `SHIPPED`.

If those steps are not completed, keep the snapshot frozen.
