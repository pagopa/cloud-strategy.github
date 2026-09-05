---
name: grill-me
description: A relentless interview to sharpen a plan or design.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it — don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report — ask the rest of the frontier now. The _decisions_ are the user's — put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

<!-- local-sync:grill-me-scope-convergence:start -->
## Scope and convergence guardrail

Narrow tree expansion without replacing the existing rounds, frontier traversal,
fact recovery, or final user-confirmation mechanics.

- Establish an interview envelope from caller context and the user's request:
  subject, desired outcome, scope, anti-scope, and requested level of detail.
- Infer the envelope when it is already clear. Ask for clarification only when
  an ambiguity would materially change the interview.
- Before every later round, admit a candidate question only when it maps to an
  unresolved user decision with settled prerequisites and its answer could
  materially change the outcome, recommendation, acceptance criteria, or a
  material risk inside the envelope.
- Prune duplicate, cosmetic, speculative, premature implementation, and
  adjacent-improvement branches.
- Treat each answer as input to the existing decisions, not implicit permission
  to broaden the subject. Park useful out-of-scope items until the user
  explicitly accepts a scope change.
- Treat the frontier as empty when no material in-scope decision remains, even
  when conceivable downstream questions exist.
- Interpret “every branch” as every material, decision-relevant branch inside
  the agreed interview envelope.
<!-- local-sync:grill-me-scope-convergence:end -->
