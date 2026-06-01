# Common Mistakes For Java Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Business logic inside controller/handler | Untestable, tightly coupled to framework | Extract to a service class, inject via constructor |
| Catching `Exception` everywhere | Swallows unexpected errors, hides bugs | Catch specific exceptions; let runtime errors propagate |
| Mutable shared state in service classes | Thread-safety bugs in concurrent environments | Use immutable objects or proper synchronization |
| No null checks on external input | NullPointerException at runtime | Validate at entry point with guard clauses |
| Test names like `test1`, `testMethod` | No documentation value, hard to diagnose failures | Use `given_when_then` naming with `@DisplayName` |
| Full `@SpringBootTest` for every test | Slow feedback and blurred failure scope | Prefer unit tests or Spring test slices first |
| Exposing JPA entities directly from controllers | Leaks persistence shape into the API and couples layers | Map entities to request/response DTOs |
| Adding virtual threads without checking execution model | Can mask blocking or context propagation issues | Adopt them only when runtime support and workload fit are clear |
| Over-using inheritance for code reuse | Rigid hierarchies, fragile base class problem | Prefer composition and delegation |
