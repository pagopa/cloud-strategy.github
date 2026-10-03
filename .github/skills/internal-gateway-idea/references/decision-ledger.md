# Decision Ledger

The compact ledger stores only:

- `Decision ID`;
- decision or constraint;
- status;
- basis;
- reopen condition;
- dependencies.

Use these states:

- `eligible-now`: open with no unresolved prerequisite;
- `blocked-later`: waiting on a prerequisite;
- `deferred`: visibly postponed by the user or an evidence limit;
- `resolved-from-evidence`: settled by sufficient local evidence;
- `accepted`: explicitly accepted by the user;
- `accepted-risk`: explicitly retained as a known risk;
- `rejected`: rejected by evidence, the user, or a supported comparison.

Use `open` only as a visible recovery marker when reconstruction fails. Root
decisions have no unresolved prerequisites. Dependents remain `blocked-later`
until prerequisites resolve. Recover local evidence before asking and move
sufficient facts to `resolved-from-evidence`.

When several roots are open, prioritize authority or scope blockers, dependency
impact, recommendation impact, material risk, then non-blocking preference.
Collect every currently known material `eligible-now` decision for the round
and map each numbered question to exactly one decision. Keep even a single
decision as a numbered one-item block. Reopen only when new evidence, an
explicit user change, or a supported critical finding matches the declared
reopen condition.
