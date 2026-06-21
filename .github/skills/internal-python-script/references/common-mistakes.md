# Common Mistakes For Python Scripts

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Missing `if __name__ == "__main__":` guard | Script runs on import, breaks testing and reuse | Always guard the entry point |
| Using a hyphenated or file-only entrypoint that cannot be imported cleanly | Breaks `python -m`, packaging, and test reuse | Expose an importable `cli.py`, package `__main__.py`, or `console_scripts` entrypoint |
| Using `print()` for errors | Errors go to stdout, mixed with normal output | Use `print(..., file=sys.stderr)` or `logging` |
| Bare `except:` or `except Exception:` at top level | Swallows all errors including KeyboardInterrupt | Catch specific exceptions; let unexpected ones propagate |
| Hardcoded file paths | Non-portable across machines | Use `argparse`, `pathlib`, or environment variables |
| No argument parsing | Caller has to modify script source to change behavior | Use `argparse` for any configurable parameter |
| Installing deps globally or without hash-locked version pinning | Non-reproducible environment and hidden setup drift | Keep dependencies in the local `requirements.txt` with exact pins and hashes |
| Adding an empty `requirements.txt` to a stdlib-only tool | Adds noise and implies missing setup steps | Omit `requirements.txt` when the script uses only the standard library |
| Updating `requirements.txt` without refreshed hashes | Breaks reproducible installs and hides dependency drift | Regenerate exact pins and hashes, then validate with `pip install --require-hashes -r requirements.txt` |
| Wrapping a stdlib-only script in Bash | Adds setup indirection without solving a real dependency problem | Document direct `python3 <script>.py` execution and skip the wrapper |
| Shipping a loose `.py` file with undocumented setup steps | Users must guess how to run the tool safely | Generate a self-contained folder and add `run.sh` plus `requirements.txt` only when external packages are needed |
| Treating a multi-entrypoint toolkit as app code just because it has `lib/` and tests | Pushes script tooling into the wrong guidance lane | Keep it in `internal-python-script` when the primary contract is still direct execution |
| Copying the same `.venv` bootstrap and dependency install code into every wrapper | Maintenance drift and inconsistent operator behavior | Use one shared `run.sh` and let thin wrappers delegate to it |
| Assuming the tool will always run from the repository root | Breaks when operators call it from subdirectories or nested paths | Resolve the repo root from an explicit `--root` or path argument when needed |
| Adding JSON output without a real machine consumer | Increases surface area and maintenance cost | Keep text output first and add `--format json` only when automation needs it |
| Defaulting to stdlib without comparing mature libraries | Leaves avoidable boilerplate, edge cases, and custom parsing logic in the script | Write the dependency decision note first and choose the option that makes the final code simpler |
| Rejecting a useful dependency just to keep dependency count low | Optimizes the wrong thing and increases custom code | Optimize for simpler final code and justified value, not dependency minimization |
| Adding `rich` because output looks nicer, without a human-facing reporting contract | Adds dependency cost without a clear user benefit and can corrupt JSON or other machine-readable output | Use `rich` for polished human-facing console reporting only, keep data output plain, and record the dependency decision |
| Forcing async or framework abstractions into a simple tool | Raises complexity without improving the script | Keep the script synchronous and direct unless concurrency is essential |
