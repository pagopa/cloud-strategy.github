# AI Runtime Operating Model

> Purpose: source-managed runtime consumption model for Codex, Copilot, ChatGPT, and other assistants that use this repository's AI customization assets. Keep cross-runtime loading, matching, and portability guidance here.

## Where Adjacent Content Belongs

- Use `docs/01-architecture.md` for the repository-specific architecture contract.
- Use `docs/02-repository-context.md` for stable local operating context that does not override policy.
- Use `AGENTS.md`, `.github/copilot-instructions.md`, and scoped `.github/instructions/*.instructions.md` for binding instruction policy.
- Use relevant `SKILL.md` files for task-specific workflow depth.

## Runtime Role

This repository is authored as a GitHub Copilot customization and governance baseline, but its assets should remain usable by multiple assistant runtimes.

Unlike `docs/01-architecture.md` and `docs/02-repository-context.md`, this file is source-managed by the standards repository and synchronized into consumer repositories.

## Supported Runtimes

| Runtime | How to use these assets |
| --- | --- |
| ChatGPT 5.5 | Read `AGENTS.md`, `.github/copilot-instructions.md`, matching `.github/instructions/*.instructions.md`, and relevant `SKILL.md` files as manual references when no automatic apply or skill tool exists. Replace prompt inputs such as `${input:request}` manually. |
| Opus 4.6 | Use the same manual-reference model as ChatGPT 5.5 unless the host environment provides native skill or instruction loading. |
| GitHub Copilot | Use repository instructions, path-scoped `.github/instructions/*.instructions.md`, prompts, wrapper agents, and skills through the native VS Code or GitHub Copilot surfaces. |
| Codex plugin for VS Code | Load the relevant `SKILL.md` files as the operational source of truth; Copilot wrapper agents are UX projections and may not be available. |
| Codex CLI | Treat skills and instructions as operational references unless the host environment provides native skill invocation. Follow repository-local validation commands before completion and do not rely on Copilot agent buttons. |

## Portability Rules

- Keep repository policy in `AGENTS.md` and `.github/copilot-instructions.md` instead of runtime-specific forks.
- Keep prompt files model-agnostic; `${input:...}` placeholders are a UI convenience, not a requirement of the policy.
- Treat `applyTo` as GitHub Copilot activation metadata. Other runtimes can still read the same instruction content as reference material.
- Treat `SKILL.md` files as workflows. If a runtime has no skill invocation tool, read the relevant skill file and follow its workflow manually.
- Treat `.github/agents/*.agent.md` files as Copilot wrapper projections around skill-owned semantics, not as the only operational source.
- Do not optimize asset wording for only ChatGPT 5.5, Opus 4.6, GitHub Copilot, or Codex unless a narrower local instruction explicitly requires that runtime.

## Matching Scoped Instructions

For runtime hosts without native Copilot instruction loading, scoped instructions remain relevant by matching the target path against each instruction file's `applyTo` metadata.

- Before editing, reviewing, or asserting policy for a known target path, identify every `.github/instructions/*.instructions.md` file whose `applyTo` glob matches that path.
- Read all matching instructions as manual references, including both repository-owned `internal-*` instructions and imported non-`internal-*` instructions.
- Treat multiple matches as intentional co-load unless the instructions directly conflict; prefer the narrower target scope when the conflict is clear.
- If the target path is not explicit, infer the artifact family only when it is obvious, such as Python, GitHub Actions, Kubernetes, Docker, or Markdown; otherwise ask for the target path before making path-scoped policy claims.
- Keep this as a discoverability and reference contract. Do not describe it as universal runtime enforcement or automatic loading outside hosts that document that behavior.

## Validation

- Run the repository validator or the closest available local checks after changing shared governance assets.
- Do not claim a runtime-specific behavior is guaranteed unless that runtime behavior was verified in the current environment or documented by the platform owner.
