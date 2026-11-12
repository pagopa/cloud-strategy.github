# GitHub.com Copilot Code Review

This file is only for GitHub.com Copilot code review.

## Comment Only On Evidenced Defects

- Comment when the diff shows a concrete defect, risk, or missing validation.
- Prioritize correctness, security, regressions, and missing tests over style.
- State the impact and the smallest safe fix in each comment.
- Report a repeated defect once, list the other locations, and raise its
  severity when the repetition widens the impact.
- When the diff lacks evidence, ask one short question instead of asserting.

## Check The Change Against Its Intent

- Compare the diff with the pull request description and linked issues. Flag
  missing requirements, behavior that contradicts the stated intent, and
  unrelated changes.
- For changed behavior, flag tests that would still pass if the change were
  wrong.
- When a contract changes, such as a schema, CLI, output, frontmatter, or
  policy, flag callers, validators, tests, and docs left on the old contract.

## Skip Noise

- Skip formatting, import order, and syntax issues that the repository's
  configured formatters, linters, and pre-commit hooks already enforce.
- Skip intentional defects in test fixtures, seeded review targets, eval packs,
  and gold outputs. Check only that the fixture matches its consuming test.
- Skip generated files unless the generator input and output disagree.

## Non-Scope

- Treat `AGENTS.md` as policy for judging the diff. Its local workflow steps,
  such as tool, graph, or planning commands, are not review findings.
- Do not ask authors to run local workflows, agents, or skills.
- Do not treat this file as instructions for coding agents, local CLIs, or
  non-review Copilot chat behavior.
