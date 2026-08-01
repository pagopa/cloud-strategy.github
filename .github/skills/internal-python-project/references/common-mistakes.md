# Common Mistakes For Python Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Business logic mixed with I/O | Makes behavior hard to test and refactor | Keep pure decisions separate from true external boundaries |
| Mutable default arguments (`def f(items=[])`) | Shares state between calls | Use a `None` default and create the value inside the function |
| bare `except:` | Catches control-flow exceptions such as `KeyboardInterrupt` and `SystemExit` | Catch the narrowest expected exception |
| Broad `except Exception` without handling, logging, or re-raise | Hides ordinary failures and partial work | Handle expected failures explicitly and let unexpected failures propagate |
| No type hints on public APIs | Makes contracts harder to understand and check | Add type hints to public signatures |
| Injecting every collaborator as a hook or alias | Hides real seams and call flow | Inject true external boundaries or variability points only |
| Copying shared helper logic across modules | Lets behavior drift across call sites | Keep the helper in its owning module and import it |
| Changing dependencies without updating the declared lock artifact | Breaks reproducible installs | Preserve the declared manager and regenerate its canonical lock |
| Tests that depend on execution order | Creates fragile, non-deterministic failures | Make each test self-contained |
| Forcing async into CPU-bound or simple flows | Adds complexity without useful concurrency | Use async for genuine I/O concurrency |
| Mocking internal implementation details | Hides regressions and couples tests to structure | Mock only true external boundaries |
| Styling project output with `rich`, emoji, tables, or panels | Mixes terminal UI with project behavior or plain data | Keep project logs neutral and render human output in an adapter |
| Silently trusting fuzzy or ambiguous parsing | Makes derived values look authoritative | Surface provenance, diagnostics, or an explicit ambiguity policy |
| Silently overwriting duplicate keys in indexes or joins | Hides data loss | Detect collisions and define an explicit merge policy |
| Mutating upstream payloads to add context | Introduces hidden side effects | Return wrappers, DTOs, or explicit context |
| Embedding full raw payloads in shareable outputs | Bloats artifacts and may leak sensitive data | Gate raw dumps behind an explicit flag or trace file |
| Treating line coverage as the goal | Inflates test volume without improving defect detection | Target changed behavior and risk-heavy paths |
| Mixing parsing, validation, orchestration, and side effects in one function | Hides branching and state | Split helpers when separation improves clarity or testability |
| Adding low-value re-export or alias shims | Hides the real owner | Import the real owner unless a compatibility boundary is documented |
