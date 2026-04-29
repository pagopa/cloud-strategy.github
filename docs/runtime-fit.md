# Runtime Fit

This repository is authored as a GitHub Copilot customization and governance baseline, but its assets should remain usable by multiple assistant runtimes.

## Supported Runtimes

| Runtime | How to use these assets |
| --- | --- |
| ChatGPT 5.5 | Read `AGENTS.md`, `.github/copilot-instructions.md`, matching `.github/instructions/*.instructions.md`, and relevant `SKILL.md` files as manual references when no automatic apply or skill tool exists. Replace prompt inputs such as `${input:request}` manually. |
| Opus 4.6 | Use the same manual-reference model as ChatGPT 5.5 unless the host environment provides native skill or instruction loading. |
| GitHub Copilot | Use repository instructions, path-scoped `.github/instructions/*.instructions.md`, prompts, agents, and skills through the native VS Code or GitHub Copilot surfaces. |
| Codex | Treat skills and instructions as operational references unless the host environment provides native skill invocation. Follow repository-local validation commands before completion. |

## Portability Rules

- Keep repository policy in `AGENTS.md` and `.github/copilot-instructions.md` instead of runtime-specific forks.
- Keep prompt files model-agnostic; `${input:...}` placeholders are a UI convenience, not a requirement of the policy.
- Treat `applyTo` as GitHub Copilot activation metadata. Other runtimes can still read the same instruction content as reference material.
- Treat `SKILL.md` files as workflows. If a runtime has no skill invocation tool, read the relevant skill file and follow its workflow manually.
- Do not optimize asset wording for only ChatGPT 5.5, Opus 4.6, GitHub Copilot, or Codex unless a narrower local instruction explicitly requires that runtime.

## Validation

- Run the repository validator or the closest available local checks after changing shared governance assets.
- Do not claim a runtime-specific behavior is guaranteed unless that runtime behavior was verified in the current environment or documented by the platform owner.
