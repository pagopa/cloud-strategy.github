# Common Mistakes For Python Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Business logic mixed with I/O (DB calls, HTTP) | Untestable, hard to refactor | Extract pure logic into service/domain modules |
| Mutable default arguments (`def f(items=[])`) | Shared state between calls — classic Python gotcha | Use `None` default + create inside function |
| Bare `except:` or `except Exception:` | Swallows `KeyboardInterrupt`, `SystemExit` | Catch specific exceptions |
| No type hints on public API | Hard to understand contracts, no static analysis | Add type hints on function signatures |
| Updating dependency requirements without refreshed hashes | Reproducible installs break or drift silently | Regenerate exact pins and hashes, then validate with `pip install --require-hashes -r requirements.txt` |
| Tests that depend on execution order | Fragile test suite, non-deterministic failures | Each test must be self-contained |
| Forcing async into CPU-bound or simple flows | Adds complexity without throughput benefit | Keep it synchronous unless I/O concurrency is the real bottleneck |
| Mocking internal implementation details | Makes tests brittle and hides real regressions | Mock only true external boundaries |
| Using `rich`, emoji, tables, or panels outside human-facing CLI adapter reporting | Mixes terminal UI with project behavior or machine-readable output such as JSON | Keep project logs neutral or structured, keep data output plain, and put `rich` reporting in a CLI adapter |
| Treating line coverage as the goal | Inflates test volume without improving defect detection | Target coverage around changed behavior and risky paths |
| God classes with 10+ methods | Hard to test, hard to reason about | Split by responsibility into focused classes |
