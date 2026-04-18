---
name: internal-writing-plans
description: Use when repository-owned work needs a plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local multi-file, Italian-default structure.
---

# Internal Writing Plans

Use this skill as the repository-owned wrapper for plan authoring in this repository.

Keep `obra-writing-plans` unchanged. This skill adds the local contract for where plans live, how they are split, what language they use, and what must stay outside the execution loop.

## When to use

- Writing or rewriting a repository-owned execution plan under `tmp/superpowers/`.
- Converting a monolithic plan into the local multi-file plan structure.
- Preparing a plan that will later be executed by `internal-executing-plans`.

## When not to use

- General design or spec work under `docs/superpowers/specs/`; use `obra-brainstorming` when that workflow is relevant.
- Local execution with no retained plan artifact.
- Imported or sync-managed planning assets; do not edit `obra-*` skills to impose this policy.

## Local plan contract

- Create or reuse a task folder named `tmp/superpowers/<clear-action-or-task-name>/`.
- Keep active execution plans in multiple numbered Markdown files by macro-category, for example `01-contesto-e-vincoli.md`, `02-implementazione.md`, and `03-validazione.md`.
- Do not keep one monolithic plan file when the work spans multiple macro-categories.
- Write those plan files in Italian by default unless the user explicitly asks for another language.
- Keep unresolved questions, doubts, and user decisions in `dubbi-e-domande.md`.
- `dubbi-e-domande.md` is not an execution-plan file and must stay outside the plan-and-apply loop.

## Relationship to OBRA

- Use this skill first for repository-owned planning policy.
- Reuse `obra-writing-plans` only for the remaining plan-authoring mechanics that do not conflict with the local contract.
- If the plan will be executed in the same repository-owned workflow, hand off to `internal-executing-plans` instead of routing directly to `obra-executing-plans`.

## Workflow

1. Choose a clear task folder name under `tmp/superpowers/`.
2. Define the macro-categories first, then create one numbered plan file per category.
3. Keep each numbered file actionable and scoped to one macro-category.
4. Put open questions and decision requests only in `dubbi-e-domande.md`.
5. Keep executable next steps in the numbered plan files without mixing unresolved questions into them.

## Validation

- The plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- There are `01-...`, `02-...`, `03-...` style plan files when more than one macro-category exists.
- Plan files are in Italian unless the user asked otherwise.
- `dubbi-e-domande.md` exists when needed and remains separate from executable plan files.
- The plan does not rely on editing imported `obra-*` skills to enforce local policy.

## Common mistakes

- Writing the whole plan in one Markdown file.
- Mixing executable checklist items with open questions.
- Putting the plan under `docs/` instead of `tmp/superpowers/`.
- Switching the whole repository to Italian instead of keeping the exception local to plan files.
