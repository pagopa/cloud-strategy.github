# Requirements and Persona Contract

Use this reference when creating an agent from a short request, materially
changing an agent's role, or defining coordinator-to-worker context transfer.

## Requirements Gate

Resolve only the inputs that materially change the agent contract:

- purpose and winning route
- expected inputs and repository evidence
- required actions and the smallest safe tool scope
- direct, coordinator, worker, or command-center role
- user invocation and subagent invocation boundaries
- risky operations, approval gates, and audit needs
- role-specific output and validation expectations

Inspect repository evidence before asking the user for facts that are already
available. Route an unresolved choice that would materially change the result
through `/grill-me` rather than an ad-hoc question. Do not force an interview
when the request and local contract already make the answer deterministic.

End the gate with one sentence that states the target role, its main boundary,
and the observable result it must produce.

## Persona Translation

Translate a vague persona request into observable behavior, not a fictional
biography.

- **Identity:** State the operating role and the problem it owns.
- **Expertise:** Name only domains that change routing, evidence selection, or
  decisions.
- **Working style:** Define how it inspects, decides, communicates, and stops.
- **Output shape:** Make required results and validation status observable.
- **Constraints:** State what it must not do and the better owner when it loses.
- **Quality bar:** Define the checks that distinguish complete work from a
  plausible-looking response.

Keep personality traits only when they change useful behavior, such as direct
severity labels in a review or cautious evidence handling in a production
workflow. Do not invent credentials, years of experience, authority, or
expertise that the contract cannot substantiate. Avoid prestige language.

Keep the operating stance concise. Put reusable procedures, large checklists,
and domain handbooks in an existing owner or a bundle-local reference instead
of expanding the agent body.

## Name and Path Safety

For a new internal agent:

1. Require a canonical identifier matching
   `^internal-[a-z0-9]+(?:-[a-z0-9]+)*$`.
2. Keep the identifier aligned across the filename stem, frontmatter `name:`,
   and command identifier.
3. Resolve the target and verify that it stays under `.github/agents/`.
4. Reject path separators, dot segments, whitespace, shell metacharacters, and
   YAML metacharacters.
5. Ask for a safe replacement when a supplied name is suspicious. Do not
   silently sanitize it.

Treat an existing target as an edit. Do not overwrite or replace it until its
current contract and user-owned changes have been inspected.

## Context Handoff

Do not assume a subagent can see the parent conversation. A coordinator must
package enough task-local context for the worker to act without reconstructing
hidden intent:

- objective and bounded scope
- relevant paths, snippets, or evidence
- applicable constraints and approval boundaries
- expected output shape
- validation required before completion

Pass raw task evidence rather than the coordinator's intended conclusion.
Exclude unrelated conversation history, secrets, and redundant repository
context. Require the worker to report unresolved gaps instead of guessing.

For repeated routing across several related workers, keep one explicit
coordinator contract and an allowlist in `agents:`. Do not create a companion
routing skill per worker merely for symmetry.

## Proportional Quality Gate

Before finalizing, confirm:

- the route is more specific than the persona label
- the tool contract supports the declared actions and no more
- the working style is actionable without becoming a long procedure
- the output contract exposes missing evidence and validation gaps
- safety rules are task-shaped rather than copied generic boilerplate
- coordinator handoffs include the minimum sufficient context
