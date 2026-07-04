---
name: superpowers-executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute tasks, write a plan state file for every terminal outcome, and report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (Claude Code, Codex CLI, Codex App, and Copilot CLI all qualify; see the per-platform tool refs in `../using-superpowers/references/`). If subagents are available, use superpowers-subagent-driven-development instead of this skill.

## Plan State File Contract

Whenever execution reaches a terminal stop, write a compact Markdown state file next to the original plan file.

**Filename:** `<plan-basename>.<STATUS>.md`

- `<plan-basename>` is the plan filename without the final `.md` suffix.
- `<STATUS>` must be one of `DONE`, `BLOCKED`, `PARTIAL`, or `NEEDS_REVIEW`.
- Before writing a new state file, remove or replace stale sibling state files for the same plan basename with one of the supported status suffixes.
- Keep the file short, normally under 40 lines.
- The main session owns the final state file, even when subagents contribute.

**Status meanings:**
- `DONE`: all planned work is complete, required verification has passed or gaps are explicitly accepted, and finishing is complete.
- `PARTIAL`: meaningful work is complete, but execution cannot be declared done because validation, finishing, or remaining plan work is unresolved.
- `BLOCKED`: execution cannot continue without user input, access, dependency, clearer instructions, or repair of a repeated non-repairable failure.
- `NEEDS_REVIEW`: initial plan review found critical gaps before implementation starts, or the plan needs user correction before safe execution.

**Required file shape:**

````markdown
# <Plan Title Or Basename> - <STATUS>

## Status
<STATUS>

## Reason
<one or two sentences explaining why this status was chosen>

## Completed
- <brief completed item, or "None">

## Remaining
- <brief remaining item, or "None">

## Validation
- <command/result pairs actually run, or explicit validation gap>

## Next
<single recommended next action>

## Resume Notes
<short notes needed to resume, including any user question or blocker detail>
````

Include only commands actually run. If validation was not run, say why.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If the plan has critical gaps before implementation: write a `NEEDS_REVIEW` state file, report the path, and raise the concern with your human partner before starting
4. If no blocking concerns remain: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers-finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

### Step 4: Write Plan State File

At every terminal stop:
1. Determine the final status from the execution outcome.
2. Build the target state filename from the plan path and status.
3. Remove or replace stale sibling state files matching the same plan basename and a supported status suffix.
4. Write the compact state file using the required shape above.
5. Report the state file path in the final chat response.

Use `DONE` only after the finishing workflow is complete. If task work is complete but finishing is not complete, use `PARTIAL` unless the human partner explicitly accepts the remaining gap.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

Before asking for clarification at a terminal stop, write the appropriate plan state file:
- Use `NEEDS_REVIEW` when the blocker is a plan-quality issue discovered before implementation.
- Use `BLOCKED` when execution cannot proceed without input, access, dependencies, or clearer instructions.
- Use `PARTIAL` when some execution work is complete but the plan cannot be declared done.

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Always write a plan state file before ending at a terminal stop
- Report the plan state file path in the final response
- `DONE` requires completed finishing, not only completed task checkboxes
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superpowers-using-git-worktrees** - Ensures isolated workspace (creates one or verifies existing)
- **superpowers-writing-plans** - Creates the plan this skill executes
- **superpowers-finishing-a-development-branch** - Complete development after all tasks
