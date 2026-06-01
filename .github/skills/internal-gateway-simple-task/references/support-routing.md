# Simple Task Support Routing

Use this reference after the quick lane is selected and support ownership is
still noisy. Keep support conditional and minimal.

## Core Rule

Load support for the first real blocker, file type, runtime, domain signal, or
validation path. Do not load a support bundle because it might become useful.
Treat a support skill's `## Referenced skills` section as an owner index, not a
reason to preload its neighbors. Follow those references only when current
evidence proves the narrower owner.
When a path helper is used, prefer the single narrowest owner proved by that
path. Do not emit a base-plus-depth stack or a referenced-skill chain for a
simple edit unless the path itself proves both owners are independently needed.

## Evidence Order

Prefer support signals in this order:

1. Explicit user-selected skill or domain.
2. File type, path family, runtime, framework, command, or schema surface.
3. Reproduced failure loop or validation output.
4. Cloud, provider, platform, or governance evidence in the prompt or files.
5. Existing nearby patterns in the same repository area.

If no strong signal exists, do not guess. Stay in the quick lane with local
repository evidence, or escalate when the missing owner changes the risk.

## Support Buckets

| Signal | Support posture | Boundary |
| --- | --- | --- |
| Missing intent, target path, input data, local context, or blocker prevents starting or continuing | Use `grill-me` only within the single-clarification limit in `references/clarification-gate.md`. | If the answer must settle ownership, rollout, governance, tradeoffs, validation strategy, or exceeds that clarification gate, escalate instead. |
| Bug, failing test, failing build, drift, or unexpected output | Use root-cause debugging support after reproducing the loop. | Do not patch from correlation alone. |
| Test-first request or executable behavior change | Use test-first support when a meaningful seam exists. | Do not force TDD onto prose, prompt, skill, inventory, or governance text without executable behavior. |
| Existing diff needs findings or merge readiness | Leave simple mode for review ownership. | Do not turn simple validation into defect-first review. |
| User asks to zoom out, understand unfamiliar code, or map modules and callers | Use `internal-high-level-review` as orientation support while staying descriptive. | Do not turn orientation into findings unless concrete systems risk is evidenced. |
| Architecture, workflow, cross-cutting impact, or blind spots dominate | Leave simple mode for systems review ownership. | Do not keep editing while ownership or rollout is unsettled. |
| Repository-owned skill, agent, prompt, or AI configuration work | Use the matching authoring owner when route, boundary, validation, or bundle structure changes. Inspect the owning bundle and nearest contract tests before calling it a pure copyedit. | Pure copyedits can remain simple after that bundle check. |
| Runtime, language, infrastructure, or platform file | Use the matching domain owner only after the path or task proves it. | Do not list or preload every possible operational skill. |
| Cloud or provider work | Use provider/domain support only when the prompt, files, commands, or validation surface identify it. | Do not infer unsupported status from an absent example. |
| Performance is the primary measured concern | Use performance support with baseline and before/after evidence. | Do not optimize from intuition alone. |
| Isolated workspace is required | Use worktree isolation support only when requested or needed to protect concurrent work. | Small answer, validation, and one-file edits should stay in the current workspace. |

## Claim Gates

Use this table when the task stays simple but the final answer would make a
strong status claim. This table is the single source of truth for claim-gate
ownership in simple mode.

| Claim before final answer | Required owner | Evidence gate |
| --- | --- | --- |
| Original bug, failure, validator drift, or loop is fixed | `internal-debugging` | Re-run the original loop, or state the blocker. |
| Red-green-refactor passed or regression coverage exists | `internal-tdd` | Show the failing-then-passing seam, or state why it could not be run. |
| Performance improved | `internal-performance-optimization` | Compare baseline and after evidence from the same measurement class. |
| PR is ready, valid, mergeable, or complete | `internal-github-pr` | Check PR lifecycle evidence before the claim. |
| No code findings or code merge-readiness blockers exist | `internal-code-review` | Defect-first review evidence, or escalate to review mode. |
| No systems findings or systems merge-readiness blockers exist | `internal-high-level-review` | Systems review evidence, or escalate to review mode. |
| Any completion, readiness, no-findings, fixed, covered, or improved claim | `superpowers-verification-before-completion` | Fresh validation evidence, not intent or stale output. |

If a required owner makes the work review-owned, staged, retained-plan-owned, or
critical-owned, stop simple mode and escalate instead of making the claim.

Treat `validator passes` as a passing claim. Re-run the validator and read
fresh output before saying it passed.

If the touched work includes auth, config, secrets, tenant data, or other
sensitive values, add a validation note confirming that nothing sensitive was
hardcoded, or state the exact gap.

## Anti-Catalog Rule

This reference is not a live inventory of repository skills. If a domain is not
named here, inspect repository evidence and available skills before deciding the
owner. The claim gates above are narrow status-claim protections, not a support
catalog. The simple gateway should stay high level while operational skills
activate only when called or proven by context.

## Advisory Helper

Run `scripts/suggest_support_skills.py` only when paths or symptoms are known and
support selection is noisy. Treat its output as hints. The agent still must
inspect local files and relevant domain skills before editing or claiming
policy.
