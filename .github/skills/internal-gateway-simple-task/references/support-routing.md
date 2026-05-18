# Simple Task Support Routing

Use this reference after the simple lane is selected. Keep support skills
conditional and minimal.

## Core Rule

Load support for the first real blocker, file type, runtime, or validation path.
Do not load a support bundle because it might be useful later.

## Support Map

| Trigger | Use | Do not use when |
| --- | --- | --- |
| Bug, failing test, failing build, validator drift, sync drift, unexpected output | `internal-debugging` | The task is only prose, prompt, agent, or skill text with no failing loop. |
| Test-first request, regression seam, executable behavior change | `internal-tdd` | The change is Markdown, prompt, agent, skill, inventory, or governance text with no executable seam. |
| Line-level code defects, regressions, tests, language anti-patterns | `internal-code-review` through review mode | The user asked to implement a known fix rather than review. |
| Architecture, workflow, cross-cutting impact, blind spots, merge risk | `internal-systems-review` through review mode | The task is a clear local edit or answer. |
| Measured latency, throughput, profiling, query-plan, or regression budget | `internal-performance-optimization` | Performance is only a guess or secondary concern. |
| Isolated workspace needed for feature work or plan execution | `superpowers-using-git-worktrees` | The task is a small local edit, answer-only work, or already isolated. |
| Python script or standalone operational tool | `internal-script-python` | The file belongs to a package/application module; use the project skill instead. |
| Python package or application module | `internal-project-python` | The file is a one-off operational script. |
| Bash script | `internal-script-bash` | The shell file is only an example in documentation. |
| Terraform | `internal-terraform` | The task is cloud strategy only and does not edit Terraform. |
| GitHub Actions workflow or composite action | `internal-github-actions`; add `internal-github-action-composite` for composite action metadata | The YAML is not a workflow or action. |
| Dockerfile or Compose | `internal-docker` | Docker is only mentioned in prose. |
| Kubernetes manifest or deployment | `internal-kubernetes` or `internal-kubernetes-deployment` | The task is cloud design without manifest edits. |
| Repository-owned skill work | `internal-skill-creator` | The change is a simple copyedit that does not affect route, boundary, validation, or bundled resources. |
| Repository-owned agent work | `internal-agent-creator` | The target is only a reusable procedure that belongs in a skill. |

## Imported Support

Do not use `mattpocock-zoom-out` as the broad-map support for simple tasks.
Architecture and cross-boundary review evidence belongs to
`internal-systems-review`. Code defect evidence belongs to
`internal-code-review`.

Imported support remains conditional for the owners that still explicitly allow
it. This simple lane should prefer internal owners for debugging, TDD,
performance, code review, and systems review.

## Worktree Isolation

Use `superpowers-using-git-worktrees` only when isolation is part of the task
shape:

- the user asks for an isolated branch or worktree
- feature work should not share the current checkout
- an approved retained plan should be executed away from the active branch
- baseline testing must be separated from local user changes

For small answer-only, validation-only, or one-file edits, work in the current
workspace and preserve unrelated user changes.

## Advisory Helper

Run `scripts/suggest_support_skills.py` when file paths or symptoms are known
and support selection is noisy. Treat its output as advisory. The agent still
must inspect local files and matching scoped instructions before editing or
claiming policy.
