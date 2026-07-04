# AGENTS.md Improvement Design

## Context

This repository uses `AGENTS.md` as the always-on operating core for coding
agents. The file is already compact and explicitly routes detailed procedures to
skills, docs, validators, and narrower owners. Local contract tests also assert
specific snippets in `AGENTS.md`, so a rewrite must preserve tested root-policy
shape unless the contract change is deliberate.

External guidance reviewed for this design:

- AIHero, "A Complete Guide To AGENTS.md": keep root guidance small, avoid stale
  file-structure detail, use progressive disclosure, and keep only guidance that
  applies to every task in the always-on file.
- Boris Cherny's `CLAUDE.md`: use plan mode for non-trivial work, offload focused
  research to subagents, verify before done, capture reusable lessons after
  correction, prefer simple root-cause fixes, and avoid unnecessary impact.

Repository evidence reviewed:

- `AGENTS.md` already separates portable shared policy from source-local rules.
- `docs/repository-context.md`, `docs/architecture.md`, and `docs/tech.md`
  describe the repository as a standards repository for AI governance and sync.
- `INTERNAL_CONTRACT.md` defines `AGENTS.md` as strategic policy, not a holder
  for command playbooks or long procedures.
- `tests/test_repository_workflow_policy_contract.py` asserts root-policy shape,
  graph orientation text, and tactical defaults.
- `tests/test_retained_learning_contract.py` keeps retained-learning ledger detail
  out of `AGENTS.md`.
- `tests/test_plan_policy_contract.py` keeps retained-plan paths and detail out of
  always-on policy.

## Decision

Use a compact hybrid improvement. Keep `AGENTS.md` as a small operating core,
not a full agent handbook. Add only universal behavior that improves every task
and is already compatible with the repository's skill-first model.

The implementation should avoid a radical AIHero-style split because this root
file is already short and current tests intentionally preserve graph and tactical
baseline text. It should also avoid copying Boris Cherny's `CLAUDE.md` structure
verbatim because task files, lesson ledgers, and plan procedures are owned by
repository-specific skills and contracts.

## Target State

`AGENTS.md` should retain its current sections and improve three areas.

First, tactical defaults should make owner discipline and validation visibility
explicit. The root file should include compact wording equivalent to:

- Keep one active primary owner per execution lane; load narrower owners only
  when path, runtime, symptom, or validation evidence proves they are needed.
- Name the validation path early; if evidence changes it, update the working
  assumption before editing.

Second, operating principles should retain root-cause and minimal-impact behavior
without becoming a full debugging playbook. Boris-style "fix the real problem"
belongs in root only as a concise principle. Detailed debugging workflow remains
owned by the debugging skills.

Third, non-trivial work should be planned without putting plan-file procedures in
root. `AGENTS.md` may say that non-trivial repository-owned work makes target
state, anti-scope, assumptions, tradeoffs, and validation path visible. It should
not name retained-plan folders, task files, or lesson-ledger rows.

## Anti-Scope

Do not add package-specific, language-specific, cloud-specific, or workflow-step
detail to `AGENTS.md`.

Do not copy Boris Cherny's task-management file paths into this repository.
Those paths conflict with local retained-plan and retained-learning contracts.

Do not remove the existing `graphify` root section unless the repository owner
also approves updating `INTERNAL_CONTRACT.md` and the contract tests that
intentionally preserve compact graph orientation rules.

Do not add live catalog entries to `AGENTS.md`. `.github/INVENTORY.md` remains
the exact live catalog.

## Architecture

The updated policy remains layered:

- `AGENTS.md`: always-on precedence, placement, tactical defaults, validation
  posture, token-drift discipline, and standards-repository locality.
- `INTERNAL_CONTRACT.md`: rule-level invariants that explain why the root shape
  exists and how validators should treat it.
- `docs/`: descriptive repository knowledge that cannot override policy.
- `.github/skills/`: detailed owner-specific procedures, including planning,
  debugging, review, language guidance, sync, and retained lessons.
- `tests/`: contract checks for root-policy shape and related owner boundaries.

This preserves AIHero's progressive disclosure principle while keeping the
repository's existing skill-first architecture intact.

## Flow

For a future coding-agent task, the intended flow is:

1. Read `AGENTS.md` for scope, precedence, owner selection, and validation
   posture.
2. Identify the nearest owner from path, prompt intent, failing behavior, or
   validation evidence.
3. Load only the relevant skill, doc, or contract surface needed for that lane.
4. Make the smallest valid change.
5. Run the closest executable validation and report any validation gap.
6. If a user correction reveals a reusable pattern, codify it through the
   retained-learning owner, not root policy.

## Error Handling

If external guidance conflicts with local contracts, local repository contracts
win unless the user explicitly asks to redesign the contract.

If the improvement would require moving graph guidance or retained-plan behavior,
pause and treat that as a separate contract migration.

If validation exposes pre-existing drift, fix only the drift that affects this
change or report it as residual risk.

## Testing

The implementation plan should use these checks:

- `pytest tests/test_repository_workflow_policy_contract.py`
- `pytest tests/test_plan_policy_contract.py tests/test_retained_learning_contract.py`
- `make token-risks`
- `graphify update .` after modifying repository code or policy assets, because
  the root policy asks agents to keep the graph current after code changes.

If the edit only changes `AGENTS.md`, the focused contract tests should run before
broader checks. If the contract text changes, update `INTERNAL_CONTRACT.md` and
tests in the same implementation.

## Recommended Implementation Shape

Use a small patch to `AGENTS.md` rather than a rewrite.

Likely edits:

- Add the two missing tactical-default bullets expected by the local contract
  tests.
- Slightly strengthen the existing root-cause and validation wording if it can be
  done without adding new sections.
- Leave `graphify` text in place, with only formatting or line-wrap cleanup if
  needed.
- Leave retained-plan and retained-learning procedure details in their owning
  skills.

This should improve agent behavior while preserving instruction budget,
progressive disclosure, and current repository contracts.

## Self-Review Notes

This design has no placeholder requirements, no unresolved scope split, and no
planned broad rewrite. The only ambiguity is whether the user wants a radical
minimal-root migration. Because the user delegated autonomous decision-making and
the repository already has tests preserving the current root shape, the compact
hybrid path is the selected design.