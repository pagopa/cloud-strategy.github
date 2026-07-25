---
name: grill-me
description: A relentless interview to sharpen a plan or design.
---

# Grill Me

## Referenced skills

- None.

## Interview Approach

Interview me relentlessly about every aspect of this plan, design, or action
context until we reach a shared understanding. Walk down each branch of the
decision tree, resolving dependencies between decisions one-by-one.

Before asking, inspect the repository, codebase, documentation, or local files for answers that can be recovered from evidence.

By default, ask the full initial question set in one numbered list.

Structure the list by decision branch and dependency order. Start with goal and scope, then constraints, architecture or options, risks and failure modes, rollout, and validation as relevant.

For each numbered question, use this format: Question, Recommendation, Why, and Default if accepted. Make the recommendation detailed enough to explain what you want to decide, why it matters, and what answer you would choose by default.

Treat your recommendations as accepted unless the user says otherwise. The user may override any recommendation by referencing the question number or giving different direction.

Do not treat accepted recommendations as the end of the grilling process. If accepted defaults create contradictions, weak assumptions, unresolved risks, or dependent decisions, surface them explicitly.

After the initial numbered list, ask one question at a time only for unresolved ambiguity, dependent follow-up decisions, or branches that cannot be settled from the user's bulk response.

A caller may override the follow-up pacing with iterative numbered blocks. When a caller declares that override, replace the default one-at-a-time follow-up with the caller's pacing.

Do not ask questions that can be answered by exploring the codebase, documentation, or local files.

End by summarizing the resolved decisions, explicit assumptions, and any
unresolved questions the user chose to accept or defer.

<!-- local-sync:guided-questions:start -->
## Local guided-question contract

This repository-owned contract overrides any earlier instruction to ask one question at a time.

- Ask all currently known questions in numbered bulk question blocks.
- Use `Question`, `Recommendation`, `Why`, and `Default if accepted` for every
  numbered question.
- Make `Recommendation` the suggested answer and `Why` its concrete rationale.
- Keep each question, recommendation, and reason brief, clear, and
  decision-ready.
- Put unresolved follow-ups in another numbered block. If only one blocking
  question remains, present it as a numbered one-item block.
<!-- local-sync:guided-questions:end -->
