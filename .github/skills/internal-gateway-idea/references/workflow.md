# Internal Gateway Idea Workflow

This workflow defines the canonical contract for `internal-gateway-idea`.

## State Machine

```mermaid
flowchart TD
    A[Request enters internal-gateway-idea] --> B[Bounded evidence pass]
    B --> X{Mandatory earlier gate skipped?}
    X -- yes --> X1[Skipped-gate recovery]
    X -- no --> C{Concrete execution request?}
    X1 --> D
    C -- yes --> C1[Specialization Checkpoint: gated]
    C -- no --> D[Idea Gate 0]
    C1 --> D
    D --> E{Intent and defaults accepted?}
    E -- no --> D
    E -- yes --> F[Assumption Challenge Gate]
    F --> G[Alternative discovery]
    G --> H[Present design direction]
    H --> I{User approves design direction?}
    I -- no --> D
    I -- yes --> J[Critical Challenge Gate]
    J --> K{Critical result}
    K -- reopen --> D
    K -- narrow --> H
    K -- continue --> L[Spec vs plan decision]
    L --> M{Decision}
    M -- spec first --> N[Ask approval for retained spec path]
    M -- direct plan --> O[Ask approval for direct plan path]
    N --> P{Approved?}
    O --> P
    P -- no --> L
    P -- yes --> Q[Load internal-gateway-writing-plans]
    Q --> R[Writing outcome only]
    R --> S[Stop before implementation execution]
```

## Gate Contract

| State | Required behavior | Forbidden behavior |
| --- | --- | --- |
| `Specialization Checkpoint: gated` | Use when the incoming ask is already a file edit, command run, validator run, implementation step, or other execution-shaped request. Name the later execution owner only as a future consequence. | Do not execute, hand off, or present the post-critical recommendation. |
| `Skipped-gate recovery` | Stop the current lane, name the first skipped mandatory gate, mark downstream artifacts draft-only, and resume at that gate. | Do not continue from an invalid later state or ask the user to approve a handoff built on skipped gates. |
| `Idea Gate 0` | Confirm the recovered intent, defaults, constraints, success criteria, validation path, and anti-scope with a visible numbered question block using `Question`, `Recommendation`, `Why`, and `Default if accepted`; evidence cannot replace Idea Gate 0. | Do not treat repository evidence alone as user approval, and do not proceed to challenge, alternatives, design, or planning until this gate is accepted. |
| `Assumption Challenge Gate` | Test whether the proposed target or solution is necessary before choosing an approach. | Do not only polish the user's proposed solution. |
| `Alternative discovery` | Present 2-3 approaches and explain why the recommended one beats the strongest rejected option. | Do not present a single-path design as inevitable. |
| `Critical Challenge Gate` | Challenge the chosen direction as its own visible gate after design-direction approval and before spec or plan writing. Reopen or narrow when the objection is material. | Do not use this gate after loading `internal-gateway-writing-plans`; an embedded critique does not satisfy Critical Challenge Gate. |
| `Spec vs plan decision` | Choose `Decision: direct plan` or `Decision: spec first`, explain why, name the rejected path, and ask for approval. | Do not load `internal-gateway-writing-plans` from the decision alone. |
| `Writing outcome only` | Load `internal-gateway-writing-plans` only after explicit user approval for the selected writing path. Stop after the delegated writing outcome. | Do not implement, edit target files, run execution commands, or invoke execution owners. |

## Approval Rules

- `procedi`, `ok`, `go`, or similar approval advances only the active visible gate.
- If the active gate is ambiguous, ask whether the user means critical review,
  retained spec or plan writing, or implementation execution.
- If a previous mandatory gate was skipped, approval words cannot heal it. Use
  `Skipped-gate recovery` and resume at the first skipped mandatory gate.
- Approval of a design direction is not approval to implement.
- Approval of `Decision: direct plan` skips a retained spec, not the user
  approval gate and not the stop-before-execution boundary.

## Routing Stability Rule

Keep the agent filename, frontmatter name, and workflow aligned.

## Local validation lane

Run `python3 scripts/audit_workflow.py` before widening to catalog-wide checks. This scoped lane must cover the bundle audit and marker consistency.
