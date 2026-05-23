---
name: "internal-execute-plan"
agent: "internal-gateway-operational-flow"
description: "Execute an approved repository-owned plan to completion with triple verification, improvement notes, and lesson routing"
---

<!-- markdownlint-disable-file MD041 -->

Plan to execute:
${input:plan:Paste the retained plan path or inline approved plan to execute}

Scope or files in scope:
${input:scope:List files, directories, systems, or catalog areas involved}

Constraints and exclusions:
${input:constraints:List non-negotiables, no-touch areas, rollout concerns, or known blockers}

Expected validation:
${input:validation:List required checks, tests, validators, or write "infer from repository evidence"}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
- [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)
- [.github/skills/internal-executing-plans/SKILL.md](../skills/internal-executing-plans/SKILL.md)
- [.github/skills/superpowers-verification-before-completion/SKILL.md](../skills/superpowers-verification-before-completion/SKILL.md)
- [.github/skills/internal-lesson-codification/SKILL.md](../skills/internal-lesson-codification/SKILL.md)
- [.github/skills/internal-agent-support-next-step/SKILL.md](../skills/internal-agent-support-next-step/SKILL.md)

Execute the plan end to end.

1. Select the `execute` or `apply-plan` entry point from `internal-gateway-operational-flow`.
2. Treat this prompt as approval to continue until every executable plan item is implemented, verified, or blocked by a real blocker.
3. Use `internal-executing-plans` when the input is an approved retained plan under `tmp/superpowers/`.
4. Do not treat `questions.md` or legacy `dubbi-e-domande.md` as executable plan content.
5. Stop and produce a next-step package only when the plan is missing, ambiguous, unsafe, out of scope, or blocked by missing user input.
6. Keep edits scoped to the plan, required adjacent contracts, and validation fixes.
7. Do not silently implement newly discovered improvement ideas unless they are necessary to complete the approved plan.

Mandatory triple check before completion:

You must check the completed work three times before reporting completion. Each check must use a distinct verification perspective, not a repeated version of the same review, and must be reported separately as `Check 1`, `Check 2`, and `Check 3`. For medium or large plans, treat all three checks as substantive completion gates. For small changes, each check may be concise, but it must still be explicit and separate. Choose stronger strategies when the repository context suggests them, but the three checks must cover at least:

1. Plan coverage: map each requested plan item or source-item ledger row to an implemented change, explicit non-action, or blocker.
2. Contract coverage: re-read changed files and relevant repository instructions to check ownership, frontmatter, links, inventory, schemas, and local conventions.
3. Evidence coverage: run the applicable validators, tests, lint commands, or closest available checks; read the output before making any success claim.

If any check fails, fix the issue and rerun the relevant check. If a check cannot run, state the exact validation gap and the closest evidence gathered. Do not collapse the three checks into one summary.

Return a compact execution report with:

1. Active phase and owner.
2. Files changed.
3. Completed plan items and any intentional non-actions.
4. Triple-check results: `Check 1`, `Check 2`, and `Check 3`, each with strategy, evidence, and gaps.
5. New improvement ideas discovered during execution, kept separate from completed work.
6. Lessons found. For each durable lesson, use `internal-lesson-codification` and report the chosen owner, resource decision, always-on status, and validation. Drop task-local notes that are not reusable.
7. Residual risk and next-step package when another visible owner should act.
