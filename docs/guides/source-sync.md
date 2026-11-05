# Change Source Synchronization Safely

Use this guide to produce and verify one source-to-target synchronization change without crossing the selected ownership boundary.

## 1. Select one target boundary

Choose the owner before reading or applying a plan:

| Target | Owner | Contract |
| --- | --- | --- |
| Consumer repository | `local-sync-repos` | [Repository sync contract](../../.github/skills/local-sync-repos/references/sync-contract.md) |
| Supported home runtime | `local-agent-sync-install-ai-resources` | [Home sync contract](../../.github/skills/local-agent-sync-install-ai-resources/references/sync-contract.md) |

Do not combine the two boundaries in one plan. They use different managed resources, state, blockers, and apply semantics.

## 2. Read the source declarations

For a consumer repository, confirm the exact managed copy paths and preserved target-local paths in the [repository sync contract](../../.github/skills/local-sync-repos/references/sync-contract.md).

For a home runtime, read the [home sync catalog](../../.github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml), [runtime support matrix](../../.github/skills/local-agent-sync-install-ai-resources/references/runtime-support-matrix.yaml), and [home sync contract](../../.github/skills/local-agent-sync-install-ai-resources/references/sync-contract.md). These files determine eligible resources, supported targets, materialization, and state ownership.

## 3. Build a plan before apply

Run consumer-repository planning from the repository root:

```bash
python3 .github/skills/local-sync-repos/scripts/sync_repos.py plan --source-root . --target-repo <path> --format compact
```

This command writes the retained plan under the target repository's `tmp/` directory but does not mutate managed target paths.

Run home-runtime planning from the repository root only when the user requested inspection of that runtime:

```bash
.github/skills/local-agent-sync-install-ai-resources/scripts/run.sh plan --targets skills --format compact
```

Use a temporary home root for tests. Do not point test execution at a real home directory.

## 4. Review operations and blockers

For a consumer repository, review every `create`, `update`, `delete`, and `preserve` operation. Resolve `dirty-managed-overlap`, `stale-plan`, and `source-contract` blockers before continuing.

For a home runtime, review linked, unlinked, copied, unchanged, and blocked resources. Resolve ownership, source, link-target, and filesystem-capability blockers instead of choosing a winner implicitly. The [error-code reference](../../.github/skills/local-agent-sync-install-ai-resources/references/error-codes.md) owns the remediation for each blocker.

## 5. Apply only the reviewed plan

For a consumer repository, use the same source and target paths as the retained plan:

```bash
python3 .github/skills/local-sync-repos/scripts/sync_repos.py apply --source-root . --target-repo <path> --format compact
```

For a home runtime, apply only the selected target family:

```bash
.github/skills/local-agent-sync-install-ai-resources/scripts/run.sh apply --targets skills --format compact
```

Do not add force, dirty-target, copied-skill fallback, or implicit prune behavior. The owning contracts define the available safety gates.

## 6. Prove convergence or recover

Build the same plan again. A consumer repository is converged when it reports no managed mutations. A home-runtime apply must verify canonical link identity or the expected content hash and then report no unresolved blockers.

If verification fails, do not replay the stale apply. Resolve the reported ownership or source condition, build a fresh plan, and review it again from step 4.

Validate contract changes with the test roots named by the [consumer sync skill](../../.github/skills/local-sync-repos/SKILL.md) or [home sync skill](../../.github/skills/local-agent-sync-install-ai-resources/SKILL.md). Keep tests isolated from real consumer repositories and home runtimes.
