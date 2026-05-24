---
name: grill-me
description: Interview the user relentlessly about a plan, design, or action context until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, confirm context before starting, or mentions "grill me".
---

# Grill Me

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

Do not ask questions that can be answered by exploring the codebase, documentation, or local files.

When this skill is used as a pre-plan or pre-start gate, leave the caller with
one explicit gate status:

- `grill-me required`: unresolved user-only decisions still block safe planning
  or action.
- `grill-me satisfied`: the user answered or accepted the required decisions.
- `grill-me not applicable`: repository evidence fully resolves the decision surface.
