# AGENTS.md - Instruction Architecture Bridge

This file is the stable entrypoint for the repository instruction architecture.

## Role

- `AGENTS.md` is the main orientation document, the cross-surface bridge, and the precedence anchor.
- Keep this file stable, strategic, and free of volatile inventory.
- Treat rules as canonical here unless a narrower scoped instruction explicitly owns an exception.

## Cross-Surface Contract

1. Use `.github/copilot-instructions.md` as the repo-wide Copilot projection.
2. Use `.github/INVENTORY.md` for the exact live catalog of instructions, prompts, skills, and agents.
3. Use `.github/instructions/` for path-specific or domain-specific projections.
4. Use `.github/prompts/`, `.github/skills/`, and `.github/agents/` only when they are relevant to the current task.
5. Keep policy, projections, and inventory separate instead of mixing them into one file.

## Precedence Model

- `AGENTS.md` owns repository-wide defaults, rule placement, and bridge behavior.
- `.github/copilot-instructions.md` projects the repo-wide behavior that must remain visible in native Copilot flows and must stay aligned with this file.
- Narrower scoped instructions may override defaults only inside their declared scope.
- When rules conflict, prefer the smallest valid scope; if scope is equal, follow the canonical rule stated here and remove the conflicting duplicate.

## Language Default

- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.
- User chat may be Italian.
- Keep language exceptions explicit and local instead of restating broader prohibitions across the catalog.

## Naming Contract

- Repository-owned resources created in `cloud-strategy.github` use the `internal-*` prefix.
- Repository-owned resources created in other repositories use the `local-*` prefix.
- Imported upstream resources keep the `<short-repo>-<original-resource-name>` form.

## Projection Rules

- Keep repo-wide Copilot behavior in `.github/copilot-instructions.md`.
- Keep local self-containment in scoped instruction files only when it improves the consumer experience and does not create drift.
- Keep volatile inventory in `.github/INVENTORY.md`, never here.
- Keep `internal-sync-*` assets sync-specific. They may reference root governance, but they do not replace canonical ownership in this file or `.github/copilot-instructions.md`.
- When a sync or catalog workflow changes a repository-wide default, update the canonical owner first and then realign downstream projections or sync surfaces in the same pass.
- Do not treat removed validators, sync scripts, contract tests, or historical aliases as active policy unless they exist on disk and are reintroduced deliberately.

## Volatile Artifacts

- Transient planning, brainstorming, and other Superpowers-generated working files must not be written under `docs/`.
- When such artifacts are needed inside this repository, write them under `tmp/superpowers/`.
