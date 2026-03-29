---
name: obra-writing-skills
description: Use when creating or revising a skill, validating whether its instructions are discoverable, or tightening a skill against ambiguity, weak triggers, and missing validation.
---

# Writing Skills

Adapted from `obra/superpowers` for this repository's GitHub Copilot catalog.

## Overview

Writing skills is test-driven process documentation. A good skill is easy to trigger, concise to load, and explicit enough that another assistant will follow it correctly under pressure.

## When to use

Use this skill when:

- creating a new skill
- importing an upstream skill into `.github/skills/`
- refactoring a vague or overlapping skill
- checking whether a skill description is strong enough to trigger correctly
- tightening a skill after validation exposed loopholes or ambiguity

Do not use this skill for:

- one-off notes that should stay in a task or issue
- repository policy that belongs in `.github/copilot-instructions.md` or `AGENTS.md`
- rules better enforced by scripts or validators than by documentation

## Core rules

- Keep frontmatter to `name:` and `description:` only unless the repository explicitly requires more.
- Make `description:` describe when to use the skill, not the full workflow inside it.
- Keep the skill body lean; move heavy reference material into local helper files only when truly needed.
- Prefer one strong skill over multiple overlapping aliases.
- Rewrite imported wording when it conflicts with GitHub Copilot terminology or repository naming rules.

## Authoring workflow

1. Define the exact problem the skill should solve.
2. Write the trigger description around symptoms and situations, not around the internal implementation steps.
3. Draft the smallest body that explains the workflow, boundaries, and validation path.
4. Check for overlap with existing skills before keeping a new identifier.
5. Validate the skill by testing whether another assistant could discover it and apply it correctly.
6. Tighten weak spots exposed by validation, especially vague triggers and missing constraints.

## Trigger design

Strong descriptions usually:

- start with `Use when`
- mention concrete symptoms, tasks, or decision points
- stay technology-agnostic unless the skill is intentionally technology-specific
- avoid summarizing the whole procedure

Weak descriptions usually:

- describe what the skill teaches instead of when to load it
- copy workflow steps into the trigger
- use vague labels such as "expert help" or "best practices"

## Validation

- Confirm `name:` matches the directory name exactly.
- Confirm `description:` explains when to use the skill in one clear sentence.
- Confirm cross-references point to assets that actually exist in this repository.
- Confirm the skill adds real workflow value instead of duplicating an existing internal or stronger upstream skill.
