# Analysis Dimensions — Detailed Checklists

## 1. Correctness analysis

- Does the code do what the change claims?
- Are edge cases handled?
- Are error paths tested?
- Is input validation present and sufficient?
- Do return types match caller expectations?
- Are concurrency assumptions safe?

## 2. Separation of concerns

| Principle | What to check |
| --- | --- |
| Business vs I/O | Is business logic cleanly separated from I/O, SDKs, and persistence? |
| Module boundaries | Are module boundaries clear and cohesive? |
| Naming clarity | Do names reflect what the code does in business terms? |
| Dependency direction | Do high-level modules avoid depending on low-level details? |
| Interface stability | Are module contracts (inputs/outputs) stable and documented? |

## 3. Architecture

| Quality | What to check |
| --- | --- |
| Separation of concerns | Are business logic, I/O, and presentation layers distinct? |
| Dependency direction | Do dependencies point inward (infrastructure → application → core logic)? |
| Coupling | Is coupling between modules explicit and minimal? |
| Cohesion | Are related concepts grouped together? |
| Extensibility | Can this design accommodate likely future changes without significant rework? |
| Testability | Can each component be tested in isolation? |
| Operational readiness | Are logs, metrics, and health checks present for production visibility? |

### Repository-local deepening lens

Use these checks when the diff changes module shape, workflow ownership, or
cross-boundary review surfaces:

| Lens | What to check |
| --- | --- |
| Locality | Does a future maintainer find the relevant knowledge, bug, and fix in one place? |
| Leverage | Does a small interface carry meaningful behavior, or do callers still need the implementation details? |
| Shallow module | Is the module mostly a pass-through whose interface is nearly as complex as the implementation? |
| Deep module | Does the module hide real complexity behind a stable, useful interface? |
| Deletion test | If the module is deleted, does complexity vanish or reappear across multiple callers? |
| Real seam | Is there more than one real adapter or caller proving the seam earns its abstraction cost? |

Do not require `CONTEXT.md`, ADR folders, or glossary updates for this repository
unless those structures already exist and the user explicitly makes them part of
the task.

### Codebase orientation lens

Use these checks when the user needs a higher-level map of unfamiliar code
instead of a defect review:

| Lens | What to check |
| --- | --- |
| Target area | Which file, module, workflow, or behavior anchors the question? |
| Domain vocabulary | Which repository terms name the relevant concepts? |
| Module map | Which modules own the behavior, and what does each one hide or expose? |
| Caller map | Which direct callers, consumers, or workflow entrypoints depend on it? |
| Flow map | What data, control, or operational path connects the modules? |
| Boundary risk | Which ownership, abstraction, or validation boundary should a future edit respect? |

Keep the map descriptive. Promote observations to findings only when concrete
evidence shows a systems risk.

## 4. Blind-spot detection

Apply lateral thinking on each dimension:

- **Temporal analysis**: Will this change cause problems at scale? After 6 months of accumulation?
- **Team dynamics**: Does this change increase onboarding friction for new team members?
- **Cross-service impact**: Could this change break consumers or upstream producers?
- **Operational burden**: What happens when this fails at 3 AM? Can on-call engineers debug it?
- **Data implications**: Are there schema changes, migration needs, or data consistency risks?
- **Security surface**: Does this change expand the attack surface?
- **Performance cliffs**: Is there a hidden O(n²) or unbounded resource consumption?
- **Configuration drift**: Are there environment-specific assumptions that break in other stages?
- **Missing observability**: Can we know if something goes wrong after deployment?
- **Alternative solutions**: Is there a fundamentally simpler approach that was not considered?
