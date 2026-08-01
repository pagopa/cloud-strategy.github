# Common Mistakes For Node.js Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Floating or unintentionally unobserved promises | Failures can disappear from the owning application flow. | Observe intentional outcomes and make fire-and-forget ownership, failure handling, and lifecycle explicit. |
| Domain logic coupled to transport handlers | Application behavior becomes difficult to reuse and test. | Move domain decisions behind application services with transport-independent inputs and results. |
| Swallowed operational errors | Callers and operators lose the information needed to recover. | Classify expected operational failures and route them through the central error path. |
| Missing boundary validation | Malformed external data reaches domain logic and causes unstable behavior. | Validate transport and adapter inputs before invoking domain operations. |
| Concurrency primitives used with incorrect dependency assumptions | Work can race, reorder, or hide partial failures. | Make dependencies explicit and choose sequential, all-or-nothing, or partial-failure behavior deliberately. |
| Framework or module-system migration without an explicit compatibility decision | Runtime behavior, imports, and test seams can break together. | Record the compatibility decision and migrate the affected boundary as one application change. |
| Mocks replacing internal behavior rather than external boundaries | Tests can pass while the real application contract is broken. | Keep internal modules real where practical and mock only external systems or adapters. |
