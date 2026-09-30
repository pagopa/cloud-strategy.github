#!/usr/bin/env python3
"""Run repository-owned static and Python validation units."""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from collections import OrderedDict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from tools.validation_core import (
    EventSink,
    RepositorySnapshot,
    RunContext,
    RunReport,
    UnitResult,
    ValidationUnit,
    render_run,
    run_command,
    run_units,
    write_run_result,
    write_unit_log,
)
from tools.validation_core.events import LiveEventWriter

DEFAULT_TMP_DIR = Path("tmp/validate-code")
DEFAULT_MAX_PARALLEL = min(4, os.cpu_count() or 1)
GLOB_CHARACTERS = frozenset("*?[")
IGNORED_PARTS = frozenset({".venv", ".terraform", "__pycache__"})


@dataclass(frozen=True)
class StaticCheck:
    name: str
    build: Callable[[RunContext], int]


@dataclass(frozen=True)
class PythonShard:
    name: str
    paths: tuple[str, ...]
    excludes: tuple[str, ...] = ()


def _expand(root: Path, pattern: str) -> set[Path]:
    base_pattern = pattern[:-3] if pattern.endswith("/**") else pattern
    if GLOB_CHARACTERS & set(base_pattern):
        return {match for match in root.glob(base_pattern) if match.exists()}
    candidate = root / base_pattern
    return {candidate} if candidate.exists() else set()


def _relative_paths(
    root: Path, patterns: Iterable[str], excludes: Iterable[str] = ()
) -> tuple[Path, ...]:
    paths: set[Path] = set()
    for pattern in patterns:
        paths |= _expand(root, pattern)
    for pattern in excludes:
        paths -= _expand(root, pattern)
    return tuple(sorted(paths))


def _run_many(context: RunContext, commands: Sequence[Sequence[str | Path]]) -> int:
    status = 0
    for command in commands:
        current = run_command(context, command)
        if current:
            status = max(status, current, 1)
    return status


def _actionlint(context: RunContext) -> int:
    workflows = sorted(
        path
        for pattern in ("*.yml", "*.yaml")
        for path in (context.root / ".github/workflows").glob(pattern)
        if path.is_file()
    )
    actionlint = shutil.which("actionlint") or "actionlint"
    return run_command(context, [actionlint, *workflows])


def _shell_targets(root: Path) -> list[Path]:
    targets: set[Path] = set()
    for pattern in (
        ".github/scripts/*.sh",
        ".github/tools/*.sh",
        ".github/skills/internal-*/scripts/**/*.sh",
        ".github/skills/local-*/scripts/**/*.sh",
        "tools/**/*.sh",
        "validate-code.sh",
    ):
        targets |= {
            candidate
            for candidate in _expand(root, pattern)
            if candidate.is_file() and not IGNORED_PARTS & set(candidate.parts)
        }
    return sorted(targets)


def _shell(context: RunContext) -> int:
    targets = _shell_targets(context.root)
    status = _run_many(context, [["bash", "-n", target] for target in targets])
    if shutil.which("shellcheck") or context.dry_run:
        status = max(
            status, run_command(context, ["shellcheck", "-s", "bash", "-x", *targets])
        )
    return status


def _python_dependencies(context: RunContext) -> int:
    return run_command(context, [sys.executable, "-m", "pip", "check"])


def _python_compile(context: RunContext) -> int:
    return run_command(
        context,
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "-x",
            r"(^|/)\.venv/",
            ".github/scripts",
            ".github/tools",
            ".github/skills",
            "tools",
            "tests",
        ],
    )


def _python_lint(context: RunContext) -> int:
    skill_tests = sorted(
        path.relative_to(context.root).as_posix()
        for path in (context.root / ".github/skills").glob("*/tests")
        if path.is_dir()
    )
    return run_command(
        context,
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            ".github/scripts",
            ".github/tools",
            "tools",
            "tests",
            *skill_tests,
        ],
    )


def _python_entrypoints(context: RunContext) -> int:
    log_analyzer = ".github/skills/local-copilot-log-analyzer/scripts/run.sh"
    tools_runner = "./.github/tools/run.sh"
    python = sys.executable
    return _run_many(
        context,
        [
            ["bash", log_analyzer, "prompt-exports", "--help"],
            ["bash", log_analyzer, "debug-logs", "--help"],
            [tools_runner, "analyze_copilot_debug_log", "--help"],
            [tools_runner, "benchmark-skill-tokens", "--help"],
            [python, ".github/tools/inventory/build-inventory.py", "--help"],
            [python, ".github/tools/catalog/validate-catalog.py", "--deep", "--help"],
            [python, ".github/tools/tokens/detect-token-risks.py", "--help"],
            [python, ".github/tools/skills/validate-internal-skills.py", "--help"],
            [python, ".github/skills/local-sync-repos/scripts/sync_repos.py", "--help"],
            [python, ".github/tools/catalog/validate-github-catalog.py", "--help"],
        ],
    )


STATIC_CHECKS = OrderedDict(
    (
        ("actionlint", StaticCheck("actionlint", _actionlint)),
        ("shell-static-analysis", StaticCheck("shell-static-analysis", _shell)),
        (
            "python-dependencies",
            StaticCheck("python-dependencies", _python_dependencies),
        ),
        (
            "python-static-analysis",
            StaticCheck("python-static-analysis", _python_compile),
        ),
        ("python-lint", StaticCheck("python-lint", _python_lint)),
        (
            "python-entrypoints",
            StaticCheck("python-entrypoints", _python_entrypoints),
        ),
    )
)

PYTHON_SHARDS = OrderedDict(
    (
        (
            "repository",
            PythonShard("repository", ("tests/**", "tools/**/tests/**")),
        ),
        (
            "skills-internal",
            PythonShard(
                "skills-internal",
                (".github/skills/internal-*",),
                excludes=(".github/skills/internal-terraform-import",),
            ),
        ),
        (
            "skills-terraform-import",
            PythonShard(
                "skills-terraform-import",
                (".github/skills/internal-terraform-import/**",),
            ),
        ),
        (
            "skills-local",
            PythonShard("skills-local", (".github/skills/local-*",)),
        ),
    )
)


def _pytest_paths(root: Path, shard: PythonShard) -> tuple[Path, ...]:
    return _relative_paths(root, shard.paths, shard.excludes)


def discover_pytest_node_ids(
    root: Path, paths: Sequence[Path] | None = None
) -> tuple[str, ...]:
    """Collect top-level node IDs without executing tests.

    Without paths, Pytest uses the configured testpaths as the canonical set.
    """

    command = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
        *(paths or ()),
    ]
    completed = subprocess.run(
        [str(value) for value in command],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode not in (0, 5):
        tail = "\n".join(completed.stdout.splitlines()[-20:])
        raise ValueError(f"Pytest collection failed ({completed.returncode}):\n{tail}")
    node_ids = {
        line.strip()
        for line in completed.stdout.splitlines()
        if "::" in line and not line.startswith("=")
    }
    return tuple(sorted(node_ids))


def validate_python_shards(root: Path) -> dict[str, tuple[str, ...]]:
    """Return the path-owned collection and reject gaps or overlaps."""

    all_nodes = set(discover_pytest_node_ids(root))
    ownership: dict[str, tuple[str, ...]] = {}
    seen: dict[str, str] = {}
    for name, shard in PYTHON_SHARDS.items():
        paths = _pytest_paths(root, shard)
        nodes = set(discover_pytest_node_ids(root, paths)) if paths else set()
        if not nodes:
            raise ValueError(f"Python shard {name} is empty")
        for node in nodes:
            if node in seen:
                raise ValueError(
                    f"Python node {node} belongs to {seen[node]} and {name}"
                )
            seen[node] = name
        ownership[name] = tuple(sorted(nodes))
    unmapped = all_nodes - set(seen)
    if unmapped:
        raise ValueError(f"Unmapped Python nodes: {', '.join(sorted(unmapped))}")
    if set(seen) != all_nodes:
        raise ValueError("Python shard union does not equal canonical collection")
    return ownership


def pytest_workers(cpu_count: int, concurrent_shards: int) -> int:
    """Share CPUs between shards that run at the same time."""

    return max(1, cpu_count // max(1, concurrent_shards))


def run_python_shard(context: RunContext, shard: PythonShard, workers: int = 1) -> int:
    paths = _pytest_paths(context.root, shard)
    if not paths:
        return 1
    xdist = ["-n", str(workers)] if workers > 1 else []
    return run_command(context, [sys.executable, "-m", "pytest", "-q", *xdist, *paths])


def _run_python_integrity(context: RunContext) -> int:
    if context.dry_run:
        return 0
    validate_python_shards(context.root)
    return 0


def _python_integrity_unit() -> ValidationUnit:
    return ValidationUnit(
        "python:integrity", "Python shard integrity", _run_python_integrity
    )


def _make_units(
    stream: str | None, args: argparse.Namespace, max_parallel: int
) -> list[ValidationUnit]:
    if args.integrity_only:
        return [_python_integrity_unit()]
    units: list[ValidationUnit] = []
    if stream in (None, "python") and not args.group and not args.leaf:
        units.append(_python_integrity_unit())
    if stream in (None, "static"):
        names = [args.leaf] if args.leaf else list(STATIC_CHECKS)
        for name in names:
            check = STATIC_CHECKS[name]
            units.append(ValidationUnit(f"static:{name}", check.name, check.build))
    if stream in (None, "python"):
        names = [args.group] if args.group else list(PYTHON_SHARDS)
        workers = pytest_workers(os.cpu_count() or 1, min(max_parallel, len(names)))
        for name in names:
            shard = PYTHON_SHARDS[name]
            units.append(
                ValidationUnit(
                    f"python:{name}",
                    f"Python shard {name}",
                    lambda context, current=shard: run_python_shard(
                        context, current, workers
                    ),
                )
            )
    return units


def _print_catalog() -> None:
    print("STATIC")
    for name in STATIC_CHECKS:
        print(f"  {name}")
    print("PYTHON")
    for name, shard in PYTHON_SHARDS.items():
        excluded = f" (excluding {', '.join(shard.excludes)})" if shard.excludes else ""
        print(f"  {name}: {', '.join(shard.paths)}{excluded}")


def _resolve_path(root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def _capture_snapshot(root: Path) -> RepositorySnapshot | None:
    try:
        return RepositorySnapshot.capture(root)
    except (OSError, ValueError):
        return None


def _unit_log_text(result: UnitResult) -> str:
    lines = [
        f"unit={result.unit.unit_id}",
        f"status={result.status or ('passed' if result.exit_code == 0 else 'failed')}",
        f"exit_code={result.exit_code}",
    ]
    for command in result.commands:
        lines.append(f"$ {command.command} [{command.exit_code}]")
        if command.stdout.strip():
            lines.append(f"stdout: {command.stdout}")
        if command.stderr.strip():
            lines.append(f"stderr: {command.stderr}")
    return "\n".join(lines)


def _prepare_report(
    results,
    context: RunContext,
    *,
    request: str,
    selectors: Sequence[str],
    before: RepositorySnapshot | None,
    artifact_dir: Path | None,
) -> RunReport:
    report = getattr(results, "report", None)
    if not isinstance(report, RunReport):
        report = RunReport(
            results=tuple(results),
            planned_units=tuple(result.unit.unit_id for result in results),
            serial_equivalent_seconds=sum(
                result.duration_seconds for result in results
            ),
            wall_clock_seconds=sum(result.duration_seconds for result in results),
            queue_seconds=sum(result.queue_seconds for result in results),
        )
    report = replace(
        report,
        request=request,
        selectors=tuple(selectors),
        context=context,
        artifact_root=artifact_dir,
        repository_before=before,
    )
    if artifact_dir is not None:
        updated_results: list[UnitResult] = []
        for result in report.results:
            reference = write_unit_log(
                result.unit.unit_id,
                _unit_log_text(result),
                artifact_dir,
            )
            updated_results.append(
                replace(result, artifacts=tuple(result.artifacts) + (str(reference),))
            )
        report = replace(report, results=tuple(updated_results))
    after = _capture_snapshot(context.root)
    delta = before.delta(after) if before is not None and after is not None else None
    return replace(
        report,
        repository_after=after,
        repository_delta=delta,
        artifacts=tuple(
            artifact for result in report.results for artifact in result.artifacts
        ),
    )


def _validation_exit(report: RunReport) -> int:
    return (
        1
        if any(
            result.exit_code != 0 or result.status in {"failed", "incomplete"}
            for result in report.results
        )
        else 0
    )


def _finish(report: RunReport, output_format: str, result_path: Path | None) -> int:
    validation_exit = _validation_exit(report)
    if result_path is not None:
        try:
            write_run_result(report, result_path)
        except Exception as error:
            print(f"validation result publication failure: {error}", file=sys.stderr)
    try:
        print(render_run(report, output_format))
    except Exception as error:
        print(f"validation renderer failure: {error}", file=sys.stderr)
    return validation_exit


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stream", nargs="?", choices=("static", "python"))
    parser.add_argument("--leaf", help="static check to run")
    parser.add_argument("--group", help="Python shard to run")
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("--max-parallel", type=int, default=DEFAULT_MAX_PARALLEL)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--tmp-dir", default=str(DEFAULT_TMP_DIR))
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument(
        "--format",
        choices=("auto", "terminal", "ci", "json", "markdown"),
        default="auto",
        dest="output_format",
    )
    parser.add_argument("--result-path")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--integrity-only", action="store_true")
    parser.add_argument("--root", default=".")
    return parser


def _argument_error(args: argparse.Namespace) -> str | None:
    if args.max_parallel < 1:
        return "--max-parallel must be positive"
    if args.leaf and args.stream != "static":
        return "--leaf is only valid for static"
    if args.group and args.stream != "python":
        return "--group is only valid for python"
    if args.integrity_only:
        if args.stream != "python":
            return "--integrity-only requires the python stream"
        if args.group or args.leaf:
            return "--integrity-only cannot be combined with another selector"
    for option, value, catalog in (
        ("leaf", args.leaf, STATIC_CHECKS),
        ("group", args.group, PYTHON_SHARDS),
    ):
        if value and value not in catalog:
            return f"unknown {option} {value!r}; valid values: {', '.join(catalog)}"
    return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    root = Path(args.root).resolve()
    if args.list:
        _print_catalog()
        return 0
    error = _argument_error(args)
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    tmp_dir = Path(args.tmp_dir)
    if not tmp_dir.is_absolute():
        tmp_dir = root / tmp_dir
    artifact_dir = _resolve_path(root, args.artifact_dir)
    result_path = _resolve_path(root, args.result_path)
    raw_arguments = list(argv) if argv is not None else sys.argv[1:]
    request = shlex.join(str(argument) for argument in raw_arguments)
    # Compact terminal output prints only the final unit lines.
    quiet = args.compact and args.output_format in ("auto", "terminal")
    sink = EventSink(writer=None if quiet else LiveEventWriter(sys.stderr).write)
    sink.emit(
        phase="preflight",
        unit_id=None,
        status="planned",
        detail=f"request={request} stream={args.stream or 'all'}",
    )
    selectors = tuple(
        value for value in (args.stream or "all", args.leaf, args.group) if value
    )
    context = RunContext(
        root,
        tmp_dir,
        args.dry_run,
        args.no_color,
        event_sink=sink,
        invocation_id=sink.invocation_id,
        selectors=selectors,
        artifact_dir=artifact_dir,
        metadata={"request": request, "rerun_prefix": "./validate-code.sh"},
        compact=args.compact,
    )
    before = _capture_snapshot(root)
    max_parallel = 1 if args.serial else args.max_parallel
    units = _make_units(args.stream, args, max_parallel)
    results = run_units(
        units, context, fail_fast=args.fail_fast, max_parallel=max_parallel
    )
    report = _prepare_report(
        results,
        context,
        request=request,
        selectors=selectors,
        before=before,
        artifact_dir=artifact_dir,
    )
    return _finish(report, args.output_format, result_path)


if __name__ == "__main__":
    raise SystemExit(main())
