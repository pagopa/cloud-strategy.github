# Workflow Maps

Use this reference when preserving or validating user-visible operational flows. These maps describe workflow semantics; Copilot agent `handoffs:` buttons are only one UI projection.

## Quick Execution

```text
+-----------------------------+
| Clear edit or deterministic  |
| local task                   |
+-----------------------------+
              |
              v
+-----------------------------+
| execute mode                 |
| - applies the change         |
| - keeps scope local          |
| - runs concrete checks       |
+-----------------------------+
              |
              v
+-----------------------------+
| Outcome with validation      |
| and residual risk            |
+-----------------------------+
```

Use this path when the target state is already known. Do not reopen strategy unless the task reveals real ambiguity.

### Temporary Execution Scratchpad

Use this mini workflow only inside `execute` mode when coordination state is
cheaper than rediscovering context during a multi-step task.

- Store the scratchpad outside the repository, such as `/tmp`, and never under
  `tmp/superpowers/`.
- Treat it as ephemeral execution state, not as a retained plan, approval
  signal, catalog item, or completion evidence.
- Skip it for simple one-owner or one-file tasks.
- Keep it compact enough to refresh at slice boundaries.

```text
scope:
anti_scope:
current_slice:
acceptance_check:
touched_files:
validation_status:
blockers:
```

Completion evidence still comes from requested scope coverage, changed-file
review, and fresh validator or test output.

### Catalog Fast Path

Use this repository-local variant for small catalog maintenance before escalating to retained planning or review.

- Triage `internal-gateway-simple-task` vs `execute` vs `plan` before loading optional references, support skills, or review lenses.
- Keep the first read budget to one owner file, one nearby validator or test, and one extra reference only when it changes the next safe action.
- If the target is a repository-owned bundle owner such as `SKILL.md`, inspect the owning bundle root plus relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` before closing coverage or intentional non-action.
- For `plan-only`, use `rg` to identify validators and focused tests; open the
  test file only when the assertion or failure output can change the plan.
- Use a short execution loop: targeted `rg` or nearby read, patch, nearby test, `make catalog-fast-check`, then `make github-catalog-validation` once at the end.
- Add `CATALOG_FAST_INCLUDE_TOKEN_RISKS=1` only when the change touches always-on guidance or shared contracts.
- Do not open a retained plan or full review mode for one-file or one-owner fixes that fit in the current turn.

## Staged Full Cycle

```text
+--------------------------------+
| Non-trivial repository-owned    |
| work or full-cycle request      |
+--------------------------------+
               |
               v
+-------------------------------+
| plan phase                     |
| - minimum evidence pass, then  |
|   Gate 0                       |
| - retained plan when justified |
| - Decision Brief projection    |
+-------------------------------+
               |
               v
+-------------------------------+
| visible critical phase when    |
| reasoning risk needs pressure  |
+-------------------------------+
               |
               v
+-------------------------------+
| checkpoint before execute or   |
| apply-plan unless preapproved  |
+-------------------------------+
               |
               v
+-------------------------------+
| execute or apply-plan          |
| - local delivery or done-*     |
|   retained-plan loop           |
+-------------------------------+
               |
               v
+-------------------------------+
| review evidence or final       |
| outcome with residual risk     |
+-------------------------------+
```

The full cycle coordinates visible phases. It is not hidden dispatch between wrapper agents.
Run the minimum evidence pass before Gate 0. If a request-changing
realignment alters scope, owner, target state, validation, rollout, or
anti-scope, rerun Gate 0 before any governance-sensitive plan output or edit.

## Planned Work

```text
+--------------------------------+
| Ambiguity, governance, rollout, |
| or repository-owned authoring   |
+--------------------------------+
               |
               v
+-------------------------------+
| plan mode                      |
| - minimum evidence pass, then  |
|   Gate 0                       |
| - decision frame               |
| - assumptions and tradeoffs    |
| - selected direction           |
+-------------------------------+
               |
               v
+-------------------------------+
| Next-step package              |
| Owner, scope, action,          |
| validation, risk               |
+-------------------------------+
               |
               v
+-------------------------------+
| execute, apply-plan, review,   |
| or critical only after         |
| visible checkpoint             |
+-------------------------------+
```

Planning output should be compact enough for the next owner or runtime to act without rediscovering the full problem.

## Audited Work

```text
+-----------------------------+
| Concrete change, artifact,   |
| or validation result exists  |
+-----------------------------+
              |
              v
+-----------------------------+
| review mode                  |
| - findings first             |
| - severity and confidence    |
| - causal layer               |
| - fix routing plan           |
+-----------------------------+
              |
              v
+-----------------------------+
| Route each actionable item   |
| to execute, plan, critical,  |
| or defer                     |
+-----------------------------+
```

Review treats missing validation as a finding, not a footnote.

## Retained Plan Application

```text
+-------------------------------+
| User invokes skill or wrapper  |
| with an approved tmp/ folder   |
+-------------------------------+
              |
              v
+-------------------------------+
| apply-plan entrypoint          |
| - load internal-executing-plans|
| - ignore questions.md         |
+-------------------------------+
              |
              v
+-------------------------------+
| done-* loop                    |
| - move completed items         |
| - preserve ledger coverage     |
| - delete empty active files    |
| - continue across plan files   |
| - stop only for blockers       |
+-------------------------------+
              |
              v
+-------------------------------+
| Check 1 plan coverage          |
| Check 2 contract coverage      |
| Check 3 evidence coverage      |
+-------------------------------+
```

Inline plans must be normalized into a retained plan or pass an explicit checkpoint before this path applies.

## Runtime Projection

| Runtime surface | Projection |
| --- | --- |
| GitHub Copilot in VS Code | Users may select wrapper agents and approve `handoffs: send=false` buttons. |
| GitHub.com or chat-only surfaces | Read this skill and use text next-step packages. |
| ChatGPT 5.5 or Opus 4.6 | Treat `SKILL.md` and references as manual operating guidance. |
| Codex plugin or Codex CLI | Load relevant skills directly; do not rely on Copilot agent UI. |

The workflow must remain understandable when no runtime can invoke a Copilot custom agent.

## Runtime Context Assembly

Use this section when a host runtime lacks native instruction, scoped-rule, or
skill loading.

1. Read `AGENTS.md` for repository-wide policy, precedence, owner visibility,
   and rule placement.
2. Read `.github/copilot-instructions.md` as the Copilot-native projection when
   the task may run in a Copilot surface or the projection affects shared
   behavior.
3. Match known target paths against `.github/instructions/*.instructions.md`
   `applyTo` metadata, then read every matching instruction as manual context.
4. Load the selected owner skill and only the support skills or references that
   can change the current phase.
5. Use repository context docs, generated inventory, retained plans, and
   `done-*` files as descriptive evidence.
6. Use fresh tool or validator output before any completion, passing, or
   no-finding claim.

Keep prompt assembly external to the repository source files. XML-style
delimiters may separate loaded context at runtime, but source assets remain
Markdown.

## Context Trust Levels

| Context type | Trust posture |
| --- | --- |
| Current user request and system or developer instructions | Binding for the current session, subject to repository policy and safety rules. |
| `AGENTS.md`, `.github/copilot-instructions.md`, and matching scoped instructions | Binding repository policy for covered paths and task domains. |
| Relevant `SKILL.md` files | Workflow guidance for the selected task owner; scoped policy wins on conflicts. |
| Repository context docs, generated inventory, retained plans, and `done-*` files | Descriptive evidence. Use them to understand state, not as canonical policy. |
| Imported or comparison material under `tmp/` | Comparative data only unless the active plan names it as evidence. |
| Tool output, validator output, and terminal logs | Fresh evidence that must be read before completion or no-finding claims. |

When context conflicts, surface the conflict and reconcile it against the
smallest valid owner instead of silently choosing the longer or newer text.
