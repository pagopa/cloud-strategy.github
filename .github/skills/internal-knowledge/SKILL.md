---
name: internal-knowledge
description: Use when creating or maintaining repository README files, architecture documentation, ADRs, documentation setup, knowledge maps, or documentation coverage.
---

# Internal Knowledge

Keep repository documentation discoverable, current, and structurally consistent. Run commands from this skill directory and pass the target repository with `--repo-root`. Install the bundle lock with `python3 -m pip install --require-hashes -r requirements.txt` before invoking inventory or check in a clean environment.

## Workflow

1. Run `audit` to check the documentation setup, ADR structure, knowledge map, component README coverage, and host-configured CI-asset presence. Pass optional `--config` when the host supplies discovery policy.
2. Select only the branches requested by the user:
	- create or refresh explicit README targets with [README maintenance](references/readme-maintenance.md);
	- create or refresh `docs/architecture.md` with [architecture maintenance](references/architecture-maintenance.md);
	- record or supersede an architectural decision with [ADR maintenance](references/adr-maintenance.md);
	- create missing documentation structure with [documentation setup](references/documentation-setup.md);
	- inspect expected documentation CI assets with [CI assets](references/ci-assets.md);
	- run repository inventory or deterministic check with [inventory and check](references/inventory-and-check.md).
3. Inspect bounded repository evidence and use `impact --target <path>` when references may need coordinated updates.
4. Write only the selected documentation. Register new documentation with `update --target <path>`.
5. Run applicable Markdown and repository validators, then run `audit` again and report remaining findings. Use `update --all` only to list candidates; re-supply approved paths with `--target` before writing.

Use `python3 scripts/knowledge.py <command> --repo-root <path> --format json`. Add `--config <path>` when a host config exists. Read [audit and impact](references/modes-audit-impact.md) or [bounded updates](references/modes-update.md) only when that branch is needed.

## Boundaries

- `audit`, `impact`, `inventory`, `check`, and `update --all` are report-only.
- `bootstrap` writes only the generated map.
- `update --target` writes only `docs/knowledge-map.yaml`.
- This skill may read host `docs/knowledge-config.yaml` and must never write it.
- Documentation authoring writes only the targets authorized by the selected reference.
- Never write `AGENTS.md`, `AGENTS.local.md`, application code, or accepted ADR bodies. Report discrepancies instead.

## House Rules

- Treat the target repository's `docs/adr/README.md` as the authoritative ADR house format when present; use the bundled [minimal MADR reference](references/madr-minimal.md) only as a portable fallback.
- Store ADRs as `NNNN-<slug>.md` and keep at most one accepted ADR per number.
- Invoke `/mattpocock-domain-modeling` when a proposed ADR still needs its terminology, alternatives, trade-offs, or decision boundary clarified. Keep file ownership and final validation in this skill.

## Optional Setup Suggestion

When a user asks how to make this skill easier to discover, you may suggest a non-blocking, user-invoked `/mattpocock-writing-for-agents` pass. That suggestion is never an agent-invocable step. Any `AGENTS.md` write it produces is outside this skill's boundary and must be performed by the user or a separately authorized owner.
