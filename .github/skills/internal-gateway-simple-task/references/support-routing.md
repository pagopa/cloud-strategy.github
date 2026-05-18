# Simple Task Support Routing

Use this reference after the quick lane is selected and support ownership is
still noisy. Keep support conditional and minimal.

## Core Rule

Load support for the first real blocker, file type, runtime, domain signal, or
validation path. Do not load a support bundle because it might become useful.

## Evidence Order

Prefer support signals in this order:

1. Explicit user-selected skill or domain.
2. Scoped instruction that applies to the target path.
3. File type, runtime, framework, command, or schema surface.
4. Reproduced failure loop or validation output.
5. Cloud, provider, platform, or governance evidence in the prompt or files.
6. Existing nearby patterns in the same repository area.

If no strong signal exists, do not guess. Stay in the quick lane with scoped
repository evidence, or escalate when the missing owner changes the risk.

## Support Buckets

| Signal | Support posture | Boundary |
| --- | --- | --- |
| Bug, failing test, failing build, drift, or unexpected output | Use root-cause debugging support after reproducing the loop. | Do not patch from correlation alone. |
| Test-first request or executable behavior change | Use test-first support when a meaningful seam exists. | Do not force TDD onto prose, prompt, skill, inventory, or governance text without executable behavior. |
| Existing diff needs findings or merge readiness | Leave simple mode for review ownership. | Do not turn simple validation into defect-first review. |
| Architecture, workflow, cross-cutting impact, or blind spots dominate | Leave simple mode for systems review ownership. | Do not keep editing while ownership or rollout is unsettled. |
| Repository-owned skill, agent, prompt, or instruction work | Use the matching authoring owner when route, boundary, validation, or bundle structure changes. | Pure copyedits can remain simple. |
| Runtime, language, infrastructure, or platform file | Use the matching domain owner only after the path or task proves it. | Do not list or preload every possible operational skill. |
| Cloud or provider work | Use provider/domain support only when the prompt, files, commands, or validation surface identify it. | Do not infer unsupported status from an absent example. |
| Performance is the primary measured concern | Use performance support with baseline and before/after evidence. | Do not optimize from intuition alone. |
| Isolated workspace is required | Use worktree isolation support only when requested or needed to protect concurrent work. | Small answer, validation, and one-file edits should stay in the current workspace. |

## Anti-Catalog Rule

This reference is not a live inventory of repository skills. If a domain is not
named here, inspect repository evidence and available skills before deciding the
owner. The simple gateway should stay high level while operational skills
activate only when called or proven by context.

## Advisory Helper

Run `scripts/suggest_support_skills.py` only when paths or symptoms are known and
support selection is noisy. Treat its output as hints. The agent still must
inspect local files and matching scoped instructions before editing or claiming
policy.
