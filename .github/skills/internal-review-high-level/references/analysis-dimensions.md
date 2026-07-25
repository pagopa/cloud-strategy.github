# Analysis Dimensions — Detailed Checklists

## Systems fit

Use these checks when a diff changes module shape, workflow ownership, or
cross-boundary behavior:

### Separation of concerns

- Are business logic, I/O, and presentation layers distinct?
- Are module boundaries clear and cohesive?
- Does dependency direction keep higher-level behavior independent of details?
- Are interfaces stable for their callers?

### Architecture

- Is coupling explicit and minimal?
- Are related concepts grouped together?
- Can likely future changes be made without significant rework?
- Can components be tested in isolation?
- Are logs, metrics, and health checks sufficient for operational visibility?

### Repository-local deepening

- **Locality:** can a maintainer find the relevant knowledge, bug, and fix in
  one place?
- **Leverage:** does a small interface hide meaningful behavior from callers?
- **Module depth:** does the module hide useful complexity rather than pass it
  through?
- **Deletion test:** would deleting the module remove complexity or reproduce it
  across callers?
- **Real seam:** do at least two real users justify the abstraction boundary?
- **Cross-boundary fit:** does the change belong in the touched owner, an
  adjacent skill, a reference, a validator, or a generated catalog artifact?

Do not require `CONTEXT.md`, ADR folders, or glossary updates unless those
structures already exist and the user explicitly asks for them.

## Architecture and orientation

When the user needs a map rather than a defect review, identify:

- **Target area:** the file, module, workflow, or behavior being explained.
- **Domain vocabulary:** repository terms naming the concepts in play.
- **Module map:** responsibilities, dependencies, and callers.
- **Caller map:** direct consumers and workflow entrypoints.
- **Flow map:** the main data, control, or operational path.
- **Boundary risk:** ownership, abstraction, and validation boundaries to
  respect.

Keep the map descriptive. Promote observations to findings only when concrete
evidence shows a systems risk.

## Blind spots

Apply lateral checks to systems-fit review:

- temporal accumulation and long-term maintenance;
- onboarding and team dynamics;
- cross-service impact and operational burden;
- data implications and configuration drift;
- security surface and performance cliffs;
- missing observability and simpler alternatives.
