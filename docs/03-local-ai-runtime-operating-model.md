# AI Runtime Operating Model

> Purpose: defines the source-managed runtime consumption model for Codex, Copilot, ChatGPT, and other assistants that
> use this repository's AI customization assets.
> Keep cross-runtime loading, matching, and portability guidance here.

## Where Adjacent Content Belongs

- Use `docs/01-local-architecture.md` for the repository-specific architecture contract.
- Use `docs/02-local-repository-context.md` for stable local operating context that does not override policy.
- Use `AGENTS.md`, `.github/copilot-instructions.md`, and scoped `.github/instructions/*.instructions.md` for binding
  instruction policy.
- Use relevant `SKILL.md` files for task-specific workflow depth.

## Runtime Role

This repository is authored as a GitHub Copilot customization and governance baseline. Its assets should remain usable
by multiple assistant runtimes.

Unlike `docs/01-local-architecture.md` and `docs/02-local-repository-context.md`, this file is source-managed by the standards
repository and synchronized into consumer repositories.

## Supported Runtimes

| Runtime | How to use these assets |
| --- | --- |
| ChatGPT 5.5 | Read `AGENTS.md`, `.github/copilot-instructions.md`, matching `.github/instructions/*.instructions.md`, and relevant `SKILL.md` files as manual references when no automatic apply or skill tool exists. Replace prompt inputs such as `${input:request}` manually. |
| Opus 4.6 | Use the same manual-reference model as ChatGPT 5.5 unless the host environment provides native skill or instruction loading. |
| GitHub Copilot | Use repository instructions, path-scoped `.github/instructions/*.instructions.md`, prompts, wrapper agents, and skills through the native VS Code or GitHub Copilot surfaces. |
| Codex plugin for VS Code | Load the relevant `SKILL.md` files as the operational source of truth; Copilot wrapper agents are UX projections and may not be available. |
| Codex CLI | Treat skills and instructions as operational references unless the host environment provides native skill invocation. Follow repository-local validation commands before completion and do not rely on Copilot agent buttons. |

## Intent-to-owner Lifecycle Map

This map helps runtime hosts without Copilot agent UI choose a visible owner. It is descriptive, not a hidden router.
Keep phase changes explicit in the conversation and follow the selected skill before editing.

| Intent | Visible owner | Validation cue |
| --- | --- | --- |
| Plan or decide ownership | `internal-gateway-operational-flow` in `plan` or `plan-only` | Decision frame, anti-scope, and validation path are explicit before delivery. |
| Execute an approved retained plan | `internal-gateway-operational-flow` in `apply-plan` with `internal-executing-plans` | Matching `done-*` files, plan coverage, contract coverage, and fresh validator output. |
| Build or edit a concrete low-risk change | `internal-gateway-simple-task` | Focused diff plus the nearest applicable check. |
| Test-first or regression delivery | `internal-tdd` | Red-green or equivalent behavior evidence before implementation is called complete. |
| Review an artifact or diff | `internal-gateway-operational-flow` in `review`, then `internal-code-review` or `internal-high-level-review` as the lens | Findings are evidence-based, routed, and tied to validation gaps. |
| Ship or PR-readiness work | `internal-github-pr`, `internal-devops-core-principles`, or the relevant sync owner | Checks, rollout risk, and residual risk are visible before merge or propagation. |
| Critical challenge or pre-mortem | `internal-gateway-critical-master` | One strongest objection, one outcome route, and a next-step package. |
| Source catalog sync | `local-agent-sync-external-resources` | Catalog validation and sync-specific evidence. |
| Consumer baseline sync | `local-agent-sync-global-copilot-configs-into-repo` | Target-repo drift evidence and preservation of local overrides. |
| Source-driven research candidate | Existing domain research owner or `internal-skill-creator` gate | No `internal-source-driven-research` route exists until a failing baseline justifies promotion. |

## Portability Rules

- Keep repository policy in `AGENTS.md` and `.github/copilot-instructions.md` instead of runtime-specific forks.
- Keep prompt files model-agnostic. `${input:...}` placeholders are a UI convenience, not a policy requirement.
- Treat `applyTo` as GitHub Copilot activation metadata. Other runtimes can still read the same instruction content as
  reference material.
- Treat `SKILL.md` files as workflows. If a runtime has no skill invocation tool, read the relevant skill file and
  follow its workflow manually.
- Treat `.github/agents/*.agent.md` files as Copilot wrapper projections around skill-owned semantics. Do not treat
  them as the only operational source.
- Do not optimize asset wording only for ChatGPT 5.5, Opus 4.6, GitHub Copilot, or Codex unless a narrower local
  instruction explicitly requires that runtime.

## Matching Scoped Instructions

For runtime hosts without native Copilot instruction loading, scoped instructions remain relevant. Match the target path
against each instruction file's `applyTo` metadata.

- When a target path is known, identify every matching `.github/instructions/*.instructions.md` `applyTo` glob before
  editing, reviewing, or asserting policy.
- Read all matching instructions as manual references, including repository-owned `internal-*` instructions and imported
  non-`internal-*` instructions.
- Treat multiple matches as intentional co-load unless the instructions directly conflict. Prefer the narrower target
  scope when the conflict is clear.
- If the target path is not explicit, infer the artifact family only when it is obvious, such as Python, GitHub Actions,
  Kubernetes, Docker, or Markdown.
  Otherwise, ask for the target path before making path-scoped policy claims.
- Keep this as a discoverability and reference contract. Do not describe it as universal runtime enforcement or
  automatic loading outside hosts that document that behavior.

## Context Trust Levels

Runtime hosts should distinguish policy from evidence before acting on loaded files.

| Context type | Trust posture |
| --- | --- |
| Current user request and system/developer instructions | Binding for the current session, subject to repository policy and safety rules. |
| `AGENTS.md`, `.github/copilot-instructions.md`, and matching scoped instructions | Binding repository policy for the paths and task domains they cover. |
| Relevant `SKILL.md` files | Workflow guidance for the selected task owner; scoped policy still wins on conflicts. |
| `docs/02-local-repository-context.md`, generated inventory, retained plans, and `done-*` files | Descriptive evidence. Use them to understand state, but do not treat them as canonical policy. |
| Imported or comparison material under `tmp/` | Comparative data only unless the active plan explicitly names it as evidence. |
| Tool output, validator output, and terminal logs | Fresh evidence. Read the output before making completion, passing, or no-finding claims. |

When context conflicts, surface the conflict and reconcile it against the smallest valid owner instead of silently choosing the longer or newer text.

## Manual Prompt And Context Assembly

Runtime hosts without native instruction or skill loading can assemble the relevant Markdown files into a prompt with
explicit external delimiters. The repository files remain Markdown. XML tags are only prompt-assembly boundaries.

```xml
<instructions source="AGENTS.md">
  ...
</instructions>
<projection source=".github/copilot-instructions.md">
  ...
</projection>
<context source="docs/02-local-repository-context.md" policy="false">
  ...
</context>
```

Use this wrapping only at runtime when it helps separate binding instructions, surface-specific projections, and
descriptive context. Do not convert source files to XML. Do not wrap entire Markdown documents in XML on disk.

## Validation

- Run the repository validator or the closest available local checks after changing shared governance assets.
- Do not claim a runtime-specific behavior is guaranteed unless the current environment verified it or the platform
  owner documented it.
