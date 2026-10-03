---
name: mattpocock-to-spec
description: Turn the current conversation into a spec and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed.
---

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run `/mattpocock-setup-matt-pocock-skills` if not.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the spec using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>

<!-- local-sync:to-spec-testing-decisions:start -->
## Local testing-decisions contract

This contract overrides conflicting seam-confirmation, testing, and readiness
instructions above. Apply it in the spec's `Testing Decisions` section.

- Separate accepted mandatory checks, optional evaluations, and proposed test
  seams. Synthesize decisions already made; do not invent mandatory checks.
  Agreement on a seam or test design alone does not require its execution.
- Prefer existing runnable checks. Behavioral skill evaluations, including
  writer-to-executor trials, are optional unless the user explicitly requires
  them. A missing optional runner must not block spec publication or planning.
  Record unperformed behavioral evaluation as `not-run`; structural validation
  does not prove behavior.
- For an explicitly required evaluation, record the established runner,
  invocation, access, judge, result-capture path, and initial spending limit
  when paid. Where evidence is missing, name the unresolved prerequisite;
  preserve the requirement without inventing availability, silently waiving it,
  or presenting the spec as ready for executable planning.
- Do not conduct a new interview or request routine seam confirmation while
  synthesizing. Record proposals and unknowns in `Testing Decisions`; a
  `ready-for-agent` label must not conceal unresolved mandatory prerequisites.
<!-- local-sync:to-spec-testing-decisions:end -->
