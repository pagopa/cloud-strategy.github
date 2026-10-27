---
description: Review checks for skill bundles covering protected imported bundles, SKILL.md frontmatter and triggers, self-containment, reachability, and tests.
applyTo: ".github/skills/**"
excludeAgent: "cloud-agent"
---

# Skill Bundle Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

## Protected Bundles

- Treat skill directories whose names do not start with `internal-` or `local-` as imported and read-only.
- Flag any change inside an imported bundle unless the pull request description declares an upstream refresh or names that bundle as an authorized edit.

## SKILL.md

- Flag missing or empty `name` or `description` frontmatter, and a `name` that differs from the directory name.
- Flag descriptions that do not state when to use the skill, and triggers that overlap a sibling skill without a routing boundary.
- Flag `/skill-name` invocations of skills that do not exist in the repository.
- Flag files under `references/`, `scripts/`, or `assets/` that no `SKILL.md` link reaches.
- Flag a mandatory rule moved behind a conditional reference. That move changes behavior.

## Self-Containment

- Flag references, scripts, fixtures, or assets that resolve outside the skill directory, including host-repository scripts, manifests, or docs. Bundles prefixed `local-` are exempt.

## Tests And Evals

- Flag behavior changes in a skill or its scripts without matching bundle tests or eval-pack updates.
- Flag tests that assert raw skill prose instead of parsed structure, script output, or evaluation cases.
- Flag eval criteria or expected outputs weakened to make a failing case pass without a stated rationale.
