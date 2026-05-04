# Agents Catalog

This folder contains custom agents for repository-owned direct-owner operations plus repo-only sync workflows.

## Resolution order

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply the explicit user request and selected agent behavior.
3. Apply matching `instructions/*.instructions.md` by path.
4. Apply referenced skill details.

## Workflow map

Quick execution:

```text
User -> internal-delivery-operator -> validation -> outcome
```

Planned work:

```text
User -> internal-planning-leader -> next-step package -> internal-delivery-operator
```

Audited work:

```text
User -> internal-delivery-operator -> internal-review-guard -> internal-delivery-operator
```

Challenged decisions:

```text
User -> internal-planning-leader -> internal-critical-master -> internal-planning-leader
```

## Owner selection

- `internal-delivery-operator`: clear local execution, deterministic realignment, concrete validation.
- `internal-planning-leader`: ambiguity, cross-boundary tradeoffs, non-trivial repository-owned authoring, rollout decisions.
- `internal-review-guard`: defect-first review, merge readiness, regression analysis, validation evidence.
- `internal-critical-master`: pre-mortem, assumption pressure test, failure modes, alternative framing.
- `local-sync-external-resources`: source-side `.github/` catalog sync, rationalization, overlap cleanup, managed external resources.
- `local-sync-global-copilot-configs-into-repo`: consumer-repository baseline propagation.

Safe fallback: use `internal-planning-leader` when two or more owners still plausibly fit.

## When not to use

- Do not use `internal-planning-leader` for banal local edits once the target state is known.
- Do not use `internal-delivery-operator` when routing, ownership, or governance is still being decided.
- Do not use `internal-review-guard` to implement fixes.
- Do not use `internal-critical-master` as a routine code reviewer.
- Do not use sync agents for ordinary local implementation outside their sync scope.

## Next steps

The four canonical agents can expose VS Code `handoffs:` buttons for user-visible transitions. The buttons keep `send: false`; the user still approves the move. Agent responses should also include a compact next-step package because some surfaces may ignore handoff buttons.

Use `Next step:` labels for planned transitions and `Next action:` labels for review remediation.

## Token budget

Pick the narrowest owner that can complete the current phase. The right agent should reduce preamble, avoid re-planning solved work, and keep output focused on the next decision or validation evidence.

## Repo-only agents

- `local-sync-external-resources`
- `local-sync-global-copilot-configs-into-repo`

PR-focused work should use the `internal-pr-editor` skill because this repository does not currently ship a dedicated PR editor agent.
