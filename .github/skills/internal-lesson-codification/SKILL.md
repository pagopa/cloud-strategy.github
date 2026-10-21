---
name: internal-lesson-codification
description: Use before adding, updating, or codifying retained lessons or lessons learned so each lesson is routed to the smallest valid canonical owner first.
---

# Internal Lesson Codification

## Referenced skills

- None.

Use this skill to decide how a newly discovered lesson should be handled before editing `LESSONS_LEARNED.md` or any always-on guidance.

This skill owns the codification workflow. It does not own the ledger row format, which stays in `LESSONS_LEARNED.md`.

## When to use

- The user asks to record, report, save, retain, or codify a lesson learned.
- A task produces a durable correction that may need to become future guidance.
- An existing `LESSONS_LEARNED.md` row is being codified, narrowed, deduplicated, disproven, or deliberately retained.
- A proposed lesson appears to affect `AGENTS.md`, `.github/copilot-instructions.md`, an agent, an instruction, a prompt, a skill, a validator, or repository-owned docs.

## When not to use

- The task is only reading the ledger for context.
- The lesson is incident-specific, task-local, secret-bearing, or too narrow to reuse.
- The user explicitly asks for a mechanical ledger-format edit and no codification decision is being made.

## Core rule

Do not default to `LESSONS_LEARNED.md`.

First try to codify the lesson in the smallest valid canonical owner. Use the ledger only for stable, reusable, repository-relevant lessons that remain pending after that check.

Do not add a lesson directly to `AGENTS.md` or `.github/copilot-instructions.md`. If a lesson appears truly repository-wide and always-on, prepare a short proposal and ask before editing either file.

## Workflow

1. Identify the lesson.
   State the reusable correction in one sentence. Drop it if it is task-local, already codified, or not durable.
2. Check existing owners.
   Look for a matching skill, scoped instruction, prompt, agent, validator, repository config, or non-README technical doc before creating anything new.
3. Choose the smallest valid owner.
   Use `references/owner-decision-tree.md` when the owner is not obvious.
4. Decide whether a new resource is needed.
   Create a new skill, instruction, prompt, agent, validator, or doc only when no existing owner can carry the need cleanly.
5. Codify or defer.
   If codifying now, update the chosen owner and do not add a duplicate ledger row. If not codifying now, add or keep one pending ledger row with the intended codification target.
6. Escalate always-on guidance only by proposal.
   For `AGENTS.md` or `.github/copilot-instructions.md`, show why narrower owners fail, what text would change, and what validation would run. Wait for approval before editing.
7. Validate the touched owner.
   Run the closest existing validator for the changed files. If no validator exists, state the gap.

## Cost of deferring

`defer` in step 5 costs nothing now and everything later: a ledger row has no owner, no deadline, and no reader. Before choosing it, read the pending table. A long run of rows that each named a codification target and never reached it is evidence about this decision, not a queue awaiting its turn.

When the lesson feels too large to codify now, it is usually several lessons; codify the part whose owner is obvious. Say whether you are deferring because the owner is undecided or because the lesson is not yet durable, so a later reader can tell an open question from a postponed decision.

## Existing backlog

Do not bulk-migrate existing pending rows unless the user explicitly asks for a backlog codification pass. Existing lessons may stay where they are while this procedure is introduced.

## Output expectations

When handling a lesson, report:

- `Lesson`: the normalized reusable correction.
- `Owner`: the chosen canonical owner, or `LESSONS_LEARNED.md` as pending fallback.
- `Resource decision`: reuse existing owner, create new owner, or no retained lesson.
- `Always-on status`: not applicable, rejected, or proposal required.
- `Validation`: command or explicit validation gap.
