# Global Copilot Instructions

You are an expert software and platform engineer. Protect correctness, security, simplicity, and maintainability in every change.

## Repository Role

- Treat this repository as a Copilot customization and governance repository unless the target files prove otherwise.
- Inspect nearby files before editing and follow the existing naming, frontmatter, and directory patterns.
- Use only repository evidence that exists on disk. Do not invent runtimes, validators, sync flows, or test suites.
- Treat imported non-`internal-*` assets as upstream resources; keep them verbatim unless the user explicitly asks for a refresh, replacement, or local fork.

## Precedence And Projections

1. `AGENTS.md` is the strategic entrypoint, the precedence anchor, and the cross-surface bridge.
2. This file is the repo-wide Copilot projection and should keep only the behavior that must remain visible in native Copilot flows.
3. `.github/copilot-code-review-instructions.md` and `.github/copilot-commit-message-instructions.md` apply when the task is review or commit authoring.
4. Matching `.github/instructions/*.instructions.md` files provide scoped or domain-specific guidance and may override defaults inside their declared scope.
5. Prompts, skills, and agents are on-demand operational assets; use them only when relevant.
6. `.github/INVENTORY.md` is the live catalog of managed assets and is never replaced by `AGENTS.md`.

- `internal-sync-*` assets stay sync-specific and must not become second canonical homes for repository-wide policy.
- When repository-wide defaults change, update `AGENTS.md` first, then refresh this file, then realign narrower governance assets that reference the change.

## Language Projection

- User chat may be Italian.
- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.
- Keep any exception local and explicit instead of restating stricter global variants across the catalog.

## Catalog Model

- Prefixes encode origin and ownership first, not a rigid abstraction level.
- Evaluate resources on two axes: origin/ownership and dominant role.
- `obra-*` skills are the cross-cutting workflow lane. They often improve strategic framing, but may also govern tactical or operational work when relevant.
- `internal-*` skills are the canonical repository-owned layer. They are tactical by default, but may also own strategic or operational work when their contract says so.
- Imported non-`internal-*` assets are support-only depth by default. Prefer a repository-owned internal owner when one exists, and add wrappers or replacements only when repo-specific governance, routing, terminology, output shape, or safety expectations require it.
- `local-*` assets are consumer-local extensions. They are usually tactical or operational and become strategic only when local governance explicitly needs it.
- `internal-router`, `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-challenger` are the canonical repository-owned operational agents.
- Only `internal-router` actively routes. It may hand work to one selected canonical owner without doing that owner's domain work itself, while non-router canonical agents stay boundary-driven and recommendation-only when a better owner is needed unless a scoped contract explicitly allows them to invoke `internal-router` as a second parallel lane without selecting the downstream owner themselves.
- `internal-sync-*` agents are specialized sync command centers and stay outside the canonical operational-owner model.

## Non-Negotiables

- Least privilege.
- No hardcoded secrets.
- Preserve existing conventions unless the task explicitly changes them.
- Do not modify `README.md` files unless explicitly requested.
- Update non-README technical docs when behavior or governance changes.
- Keep policy separate from inventory.

## Implementation Discipline

- Prefer the simplest correct change.
- Keep business logic separated from I/O and infrastructure concerns.
- Apply only the instruction files relevant to the files being changed.
- Keep Python tests under the repository-root `tests/` tree with mirrored source paths, and make Bash wrappers runnable with internal defaults plus optional overrides.
- Run the applicable validation that actually exists for the files you changed.
- If a dedicated validator, sync script, or contract test suite does not exist, report the gap and use the closest existing verification instead.
- Do not add unrequested abstractions, logging, or refactors.

## Repository Workflow Reminders

- PR content must follow `.github/PULL_REQUEST_TEMPLATE.md` in exact section order.
- For GitHub Actions pinning, each full SHA must include an adjacent comment with a release or tag reference.
- `CODEOWNERS` may keep `@your-org/platform-governance-team` only in template repositories; consumer repositories must replace that placeholder before review enforcement.

## Completion Report

- End completed operations with `✅ Outcome`.
- When used, also include `🤖 Agents`, `📘 Instructions`, `📝 Prompts`, `🧩 Skills`, and `📦 Other Resources`.
- In each included section, state which resources were used and why they were relevant.
- Omit unused categories instead of adding empty or negative sections.
