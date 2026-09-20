# Knowledge Audit

Use this reference for the explicit `audit` mode selected by [knowledge scope](knowledge-scope.md). It owns the bounded read-only procedure and report shape; it does not authorize or perform documentation changes.

## Purpose

An audit answers a bounded question about current documentation, evidence, ownership, or portability. It distinguishes what was inspected from what was not inspected and reports findings without silently turning diagnosis into an authoring request.

## Boundary

Audit is read-only and non-persistent by default. It must not:

- edit, create, delete, rename, or format files;
- persist an audit report unless the caller explicitly requests a report artifact in a separate write-authorized request;
- invoke `help`, `targeted`, `sync`, or `setup` authoring;
- install tools, regenerate graphs, refresh generated content, or change ADR status;
- alter remote state, call a remote mutation, or claim a remote result that was not observed; or
- implement a finding or promote a suggestion into repository policy.

A possible fix may be recorded as a next action, but it is never applied by the audit. A separate request must name the authoring destination and owner.

## Scope And Evidence

Start with the normalized files or directories explicitly named by the caller. If the request has no bounded perimeter, ask one focused scope question before reading content. Do not infer a repository-wide audit from a generic request.

Read only the named perimeter and directly referenced local evidence needed to explain a finding. Every supporting read is part of actual coverage. Record paths that were excluded, unavailable, or outside the request rather than silently expanding the audit.

Classify evidence before drawing a conclusion:

| Evidence class | Question answered |
| --- | --- |
| Current content | What does the inspected artifact say now? |
| Ownership and provenance | Which document, owner, or generated source is authoritative? |
| Contract and structure | Which links, required shapes, or public projections can be checked locally? |
| Decision and generated protection | Is an accepted decision or generated block protected from direct edits? |
| Enforcement and validation | Which existing check covers the finding, and what remains an enforcement gap? |

String presence alone is structural evidence, not proof that the behavior is semantically coherent. When sources contradict one another, retain the contradiction as a finding with both pieces of evidence and do not invent a resolution.

## Procedure

1. State the question, normalized perimeter, and any explicit exclusions.
2. Read the perimeter and classify each material observation by evidence class.
3. Run only cheap, local supporting checks that are directly relevant and already available. Do not install a missing tool or regenerate an artifact to improve coverage.
4. Compare observations with the owning contract and identify contradictions, missing evidence, stale ownership, portability issues, or protected-content risks.
5. Prioritize findings by impact and confidence. Separate an observed defect from an unknown that needs evidence and from a suggestion that needs owner judgment.
6. Report actual coverage and limits before proposing next actions. Stop when the bounded question is answered or when the next check would require scope, authority, or external access that the audit does not have.

## Report Shape

Use this compact report shape for every audit:

### Question And Outcome

State the bounded question and whether the inspected perimeter is clear, contains findings, or is blocked by missing authority or evidence.

### Coverage And Exclusions

List the exact files or directories inspected, supporting reads, checks executed, excluded paths, unavailable tools or evidence, and unknown remote or runtime behavior. A partial audit must say what wider concern remains outside the perimeter.

### Prioritized Findings

For each finding, include:

- priority: `high`, `medium`, or `low`;
- observed evidence and its path or source;
- impact on the stated reader or owner outcome;
- confidence and any competing interpretation; and
- the smallest next action and its responsible owner, if known.

Do not turn a finding into a patch, a policy decision, or a completion claim.

### Unknowns And Next Actions

Name unresolved questions separately from findings. Keep next actions bounded: one action may request owner review, a separate authoring invocation, or an external check, but it may not silently expand the current audit.

### State And Persistence

End by stating whether files changed. The normal answer is that the audit made no changes and did not persist a report. If a caller explicitly authorized a report artifact, that request belongs to a separate authoring scope and must name its destination before any write occurs.
