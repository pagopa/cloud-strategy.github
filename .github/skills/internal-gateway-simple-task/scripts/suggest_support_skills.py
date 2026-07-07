#!/usr/bin/env python3
"""Suggest generic method hints for internal-gateway-simple-task."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SYMPTOM_METHODS = {
    "blocked": ("clarify", "A blocker needs one focused clarification before continuing."),
    "bug": ("diagnose", "Unexpected behavior needs reproduction before patching."),
    "test-failure": ("diagnose", "A failing test needs root-cause diagnosis."),
    "build-failure": ("diagnose", "A failing build needs root-cause diagnosis."),
    "validator-drift": ("diagnose", "Validator drift needs a reproducible loop."),
    "unexpected": ("diagnose", "Unexpected output needs diagnosis before patching."),
    "missing-context": ("clarify", "Missing context prevents starting the current lane."),
    "tdd": ("load-internal-tdd", "Executable behavior should route through internal-tdd before implementation."),
    "performance": ("measure-performance", "Performance is the primary measured concern."),
    "pr-readiness": ("lifecycle-check", "Readiness claims need lifecycle evidence before the final answer."),
    "code-review": ("review-shape-stop", "The work is becoming findings-first rather than execution-first."),
    "systems-review": ("review-shape-stop", "Cross-boundary analysis is dominating the task."),
    "completion-claim": ("verify-claim", "Completion or readiness claims need fresh validation evidence."),
    "no-findings": ("review-shape-stop", "No-findings claims need findings-first evidence."),
    "worktree": ("isolate-workspace-needed", "The task may need isolated workspace protection."),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest generic support methods for a concrete simple task."
    )
    parser.add_argument("paths", nargs="*", help="Target files or directories.")
    parser.add_argument(
        "--symptom",
        action="append",
        choices=sorted(SYMPTOM_METHODS),
        default=[],
        help="Known task symptom. Repeatable.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def add(suggestions: dict[str, set[str]], method: str, reason: str) -> None:
    suggestions.setdefault(method, set()).add(reason)


def normalize_path_text(path_text: str) -> str:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        repo_root = Path.cwd().resolve()
        try:
            return path.resolve().relative_to(repo_root).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def suggest_for_path(path_text: str, suggestions: dict[str, set[str]]) -> None:
    normalized = normalize_path_text(path_text)
    lowered = normalized.lower()
    name = Path(normalized).name.lower()
    suffix = Path(lowered).suffix

    if normalized.startswith(".github/skills/internal-") or normalized.startswith(".github/agents/internal-"):
        add(suggestions, "bundle-contract-check", "Repository-owned bundle paths need contract and local-validator attention.")
    if name == "codeowners":
        add(suggestions, "governance-check", "Ownership files need governance-aware validation.")
        return
    if name in {"makefile", "gnumakefile"} or suffix == ".mk":
        add(suggestions, "command-surface-check", "Build orchestration files need focused command validation.")
        return
    if "/workflows/" in lowered or "/actions/" in lowered:
        add(suggestions, "automation-check", "Automation files need focused workflow validation.")
        return
    if suffix in {".py", ".sh", ".go", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".java"}:
        add(suggestions, "load-internal-tdd", "Executable source files should route through internal-tdd before implementation.")
        add(suggestions, "runtime-check", "Executable source files need the closest runnable or syntax validation.")
        return
    if suffix in {".yml", ".yaml", ".json", ".tf"}:
        add(suggestions, "config-check", "Configuration files need schema-aware or command-aware validation.")
        return
    if suffix == ".md":
        add(suggestions, "authoring-check", "Prose bundles need contract consistency and compact evidence.")


def render_text(suggestions: dict[str, set[str]]) -> None:
    if not suggestions:
        print("No deterministic method hint. Inspect local evidence and choose the smallest bounded next move.")
        return
    for method in sorted(suggestions):
        reasons = "; ".join(sorted(suggestions[method]))
        print(f"- {method}: {reasons}")


def render_json(suggestions: dict[str, set[str]]) -> None:
    payload = [
        {"method": method, "reasons": sorted(reasons)}
        for method, reasons in sorted(suggestions.items())
    ]
    print(json.dumps(payload, indent=2))


def main() -> int:
    args = parse_args()
    suggestions: dict[str, set[str]] = {}
    for symptom in args.symptom:
        method, reason = SYMPTOM_METHODS[symptom]
        add(suggestions, method, reason)
    for path_text in args.paths:
        suggest_for_path(path_text, suggestions)

    if args.format == "json":
        render_json(suggestions)
    else:
        render_text(suggestions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
