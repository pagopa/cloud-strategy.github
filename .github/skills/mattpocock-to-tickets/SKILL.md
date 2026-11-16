---
disable-model-invocation: true
name: mattpocock-to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/mattpocock-setup-matt-pocock-skills`.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets. **How** depends on the tracker `/mattpocock-setup-matt-pocock-skills` configured; the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `tmp/.issues/<feature-slug>/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. If the source was an existing issue, make each ticket its sub-issue (tracker doc's operation). Apply the `ready-for-agent` triage label unless instructed otherwise; the tickets are agent-grabbable by construction.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit this section when blockers were set as native edges.

</issue-template>

In either form, avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

<!-- local-sync:spec-tracker-paths:start -->
## Local specification and tracker paths

This contract overrides conflicting storage defaults, publication destinations,
and spec lookup instructions above.

- Read applicable repository policy and `docs/agents/issue-tracker.md` before
  publishing or locating records. Preserve intentional custom paths and remote
  workflows; an old standard-default declaration is not a custom exception.
- Local defaults: specs use `.specs/<area>/<topic>/<feature>/spec.md`;
  implementation tickets use `tmp/.issues/<area>/<topic>/<feature>/<NN>-<slug>.md`,
  numbered from `01` per feature, with a link to their durable source.
  Incoming issues stay durable under `.issues/`; templates stay in
  `.specs/_templates/` and `.issues/_templates/`.
- Scope: use the nearest common approved Area/Topic. Omit Topic for Area-wide
  work and Area for cross-Area work or when no Areas are declared. Keep
  `Area:` with all affected values and `Topic:` when applicable. Uncertain
  applicability blocks publication; report it without inventing scope or
  starting a new interview. Feature directories are leaves, not scope parents;
  resolve path collisions before writing. Create no empty scope trees.
- Discovery: recursively scan `.specs/**/spec.md`, configured incoming issue
  records under `.issues/`, and `tmp/.issues/**/*.md` for configured `Status:`
  roles. Exclude every `_`-prefixed path segment, templates and examples.
  Implementation frontiers include only the selected feature's tickets.
- Retention: keep specs, incoming issues and templates eligible for version
  control; report conflicting ignore rules. Ticket comments and execution state
  in `tmp/` are temporary. Requirements and acceptance criteria must already
  have an authorized durable spec or equivalent source; otherwise propose it
  and stop until approved. Durable records must not depend on temporary tickets
  to retain their meaning. Never stage, commit or delete records automatically.
- Migration: old standard-default records require migration before affected
  tracker writes, even when a guide still declares the old default. Obtain
  approval for each source, destination, removal and reference repair, preserve
  state and content, and retain unique requirements durably before moving
  implementation tickets into `tmp/`. Without approval, stop affected writes.
  Read-only operations only report the requirement; unrelated docs stay unblocked.
  Preserve genuine custom paths and remote trackers; do not modify Wayfinder
  or plans in `tmp/.plans/`.
- Readers honor an explicit source reference first, then configured lookup;
  default spec lookup is recursive under `.specs/`, never inferred from folder
  existence. Report ambiguous matches. Do not duplicate remote records locally,
  create `tracker/` or `docs/.specs/`, or copy specs into ticket directories.
<!-- local-sync:spec-tracker-paths:end -->
