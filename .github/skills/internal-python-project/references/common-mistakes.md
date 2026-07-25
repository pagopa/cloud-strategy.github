# Common Mistakes For Python Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Business logic mixed with I/O (DB calls, HTTP) | Untestable, hard to refactor | Extract pure logic into service/domain modules |
| Mutable default arguments (`def f(items=[])`) | Shared state between calls — classic Python gotcha | Use `None` default + create inside function |
| bare `except:` | Also catches control-flow exceptions such as `KeyboardInterrupt` and `SystemExit` | Catch the narrowest expected exception |
| Broad `except Exception` without handling, logging, or re-raise | Can hide ordinary application failures and leave partial work unexplained | Handle expected failures explicitly and let unexpected failures propagate |
| No type hints on public API | Hard to understand contracts, no static analysis | Add type hints on function signatures |
| Injecting every collaborator as a `*_fn` hook or alias shim | Hides real seams and makes call flow harder to follow | Inject only true external boundaries or variability points; call stable helpers directly |
| Copying shared helper logic across modules | Fixes drift and behavior diverges across call sites | Define the helper once in the owning module and import it |
| Changing dependencies without updating the declared manager's lock artifact | Reproducible installs break or drift silently | Preserve the declared dependency manager; for pip, regenerate exact pins and hashes, and otherwise use its canonical frozen or locked validation command |
| Tests that depend on execution order | Fragile test suite, non-deterministic failures | Each test must be self-contained |
| Forcing async into CPU-bound or simple flows | Adds complexity without throughput benefit | Keep it synchronous unless I/O concurrency is the real bottleneck |
| HTTP client pools smaller than worker or task concurrency | Work queues behind the pool and hides throughput bottlenecks | Size connection pools and limits to match max worker or async concurrency |
| Claiming pending futures will fast-fail work that is already running | Misstates `concurrent.futures` cancellation semantics and hides partial execution | State cancellation limits honestly and handle already-running work explicitly |
| Mocking internal implementation details | Makes tests brittle and hides real regressions | Mock only true external boundaries |
| Using `rich`, emoji, tables, or panels outside human-facing CLI adapter reporting | Mixes terminal UI with project behavior or machine-readable output such as JSON | Keep project logs neutral or structured, keep data output plain, and put `rich` reporting in a CLI adapter |
| Silently trusting fuzzy or ambiguous parsing | Derived values look authoritative without provenance | Mark derived values explicitly and surface provenance or diagnostics |
| Repeating coupled labels, order, or rank literals in multiple places | Values drift and sorting bugs appear | Keep coupled value and ordering in one `Enum` or mapping source of truth |
| Building indexes or joins that silently overwrite duplicate keys | Collisions hide data loss and make debugging hard | Detect duplicate keys and surface a diagnostic or explicit merge policy |
| Mutating upstream payloads to smuggle context | Hidden side effects blur ownership and break reuse | Return wrappers, dataclasses, DTOs, or explicit context alongside the payload |
| Embedding full raw payloads in shareable outputs | Bloats artifacts and can leak sensitive data | Gate raw dumps behind an explicit flag or trace file; keep default reports summarized |
| Treating line coverage as the goal | Inflates test volume without improving defect detection | Target coverage around changed behavior and risky paths |
| God classes with 10+ methods | Hard to test, hard to reason about | Split by responsibility into focused classes |
| God functions that mix parsing, validation, orchestration, and side effects | Hidden branching and state make reuse and testing harder | Split the function into focused helpers with one responsibility each |
| Adding low-value re-export or alias shim modules | Hides the real owner and adds import indirection | Import the real owner directly unless a compatibility boundary is documented |
