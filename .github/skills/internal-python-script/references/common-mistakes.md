# Common Mistakes For Python Scripts

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Missing `if __name__ == "__main__":` guard | Runs the script on import and breaks reuse | Guard the entrypoint |
| A file-only or hyphenated entrypoint that cannot be imported | Breaks `python -m`, packaging, and focused tests | Expose an importable `cli.py`, `__main__.py`, or console entrypoint |
| `print()` for errors | Mixes errors with normal stdout | Use stderr or logging |
| bare `except:` at the script boundary | Catches `KeyboardInterrupt` and `SystemExit` | Catch the narrowest expected exception |
| Broad `except Exception` without handling, logging, or re-raise | Hides ordinary failures and partial work | Handle expected failures and let unexpected failures propagate |
| Hardcoded paths or no argument parsing when inputs vary | Makes the tool non-portable and requires source edits | Use `argparse`, `pathlib`, or an explicit configuration boundary when inputs require it |
| Dependency installation outside the declared manager or without a lock | Creates hidden, non-reproducible setup drift | Preserve the manager and its exact pins and hashes |
| Empty `requirements.txt` for a stdlib-only tool | Implies setup work that does not exist | Omit it until an external library is justified |
| Bash wrapper around a stdlib-only script | Adds indirection without a contract benefit | Document direct Python execution unless a repository runner is required |
| Loose script with undocumented setup | Forces operators to guess safe invocation | Document a self-contained layout only when the tool needs it |
| Multi-entrypoint toolkit routed to application guidance only because it has `lib/` or tests | Misclassifies direct-execution behavior | Route by the primary direct-execution contract |
| Repeated `.venv` bootstrap in wrappers | Creates inconsistent setup behavior | Use one existing shared runner when one exists |
| Assuming the current directory is the repository root | Breaks nested invocation | Resolve the root from an explicit path when needed |
| Adding JSON without a real machine consumer | Increases surface area and maintenance | Keep text as the default and add formats only for consumers |
| Adding `rich` only because output looks nicer | Adds dependency cost and can corrupt machine output | Use it only for a human-facing reporting contract and record the decision |
| Forcing async or framework abstractions into a simple tool | Raises complexity without benefit | Add them only for real I/O concurrency or a framework-owned boundary |
