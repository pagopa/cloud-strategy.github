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
| - grill-me when needed         |
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
| - ignore dubbi-e-domande.md   |
+-------------------------------+
              |
              v
+-------------------------------+
| done-* loop                    |
| - move completed items         |
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
