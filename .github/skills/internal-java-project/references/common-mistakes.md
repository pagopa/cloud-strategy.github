# Common Mistakes For Framework-Neutral Java Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Business logic mixed with I/O or transport concerns | Hard to test and change safely | Extract a framework-neutral collaborator around the domain behavior |
| Catching `Exception` everywhere | Swallows unexpected errors and hides bugs | Catch specific failures and preserve the established error contract |
| Mutable shared state without an ownership model | Thread-safety bugs in concurrent environments | Use immutable state or an explicit synchronization strategy |
| External input reaches domain code without validation | Invalid state fails far from its source | Validate at the public boundary with the repository's established contract |
| Hidden required dependencies or collaborator construction | Dependencies are difficult to reason about and replace | Make required collaborators explicit and keep composition visible |
| Tests prove only implementation details | Refactors break tests without protecting behavior | Assert observable service, module, API, or boundary outcomes |
| Unbounded concurrency or downstream work | Resource exhaustion and unstable latency | Bound work and validate representative load against downstream limits |
| Over-using inheritance for code reuse | Rigid hierarchies and fragile base-class coupling | Prefer composition and delegation |
