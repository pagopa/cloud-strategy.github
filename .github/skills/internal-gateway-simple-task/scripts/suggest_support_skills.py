#!/usr/bin/env python3
"""Suggest minimal support skills for internal-gateway-simple-task.

The script is advisory. It maps known paths and symptoms to likely repository
support owners, then leaves final selection to repository evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SYMPTOM_SKILLS = {
    "bug": ("internal-debugging", "Bug or unexpected behavior needs reproduction."),
    "test-failure": ("internal-debugging", "A failing test needs root-cause diagnosis."),
    "build-failure": ("internal-debugging", "A failing build needs root-cause diagnosis."),
    "validator-drift": ("internal-debugging", "Validator drift needs a reproducible loop."),
    "unexpected": ("internal-debugging", "Unexpected output needs diagnosis before patching."),
    "tdd": ("internal-tdd", "Executable behavior should be delivered test-first."),
    "performance": ("internal-performance-optimization", "Performance is the primary measured concern."),
    "code-review": ("internal-code-review", "Line-level code review evidence is requested."),
    "systems-review": ("internal-systems-review", "Cross-boundary or architecture review evidence is requested."),
    "worktree": ("superpowers-using-git-worktrees", "The task needs isolated workspace setup."),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest support skills for a concrete simple task."
    )
    parser.add_argument("paths", nargs="*", help="Target files or directories.")
    parser.add_argument(
        "--symptom",
        action="append",
        choices=sorted(SYMPTOM_SKILLS),
        default=[],
        help="Known task symptom. Repeatable.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def add(suggestions: dict[str, set[str]], skill: str, reason: str) -> None:
    suggestions.setdefault(skill, set()).add(reason)


def suggest_for_path(path_text: str, suggestions: dict[str, set[str]]) -> None:
    normalized = Path(path_text).as_posix()
    lowered = normalized.lower()
    name = Path(normalized).name.lower()
    suffix = Path(lowered).suffix

    if normalized.startswith(".github/skills/internal-"):
        add(suggestions, "internal-skill-creator", "Repository-owned skill path.")
    if normalized.startswith(".github/agents/internal-"):
        add(suggestions, "internal-agent-creator", "Repository-owned agent path.")
    if normalized.startswith(".github/instructions/"):
        add(suggestions, "internal-copilot-instructions-creator", "Scoped instruction path.")

    if suffix == ".py":
        if "/scripts/" in lowered or lowered.startswith(".github/scripts/"):
            add(suggestions, "internal-script-python", "Python operational script path.")
        else:
            add(suggestions, "internal-project-python", "Python package or application path.")
    elif suffix == ".sh":
        add(suggestions, "internal-script-bash", "Bash script path.")
    elif suffix == ".tf":
        add(suggestions, "internal-terraform", "Terraform file path.")
    elif suffix in {".js", ".cjs", ".mjs", ".ts", ".tsx"} or name in {
        "package.json",
        "tsconfig.json",
    }:
        add(suggestions, "internal-project-nodejs", "Node.js or TypeScript path.")
    elif suffix == ".java" or name in {"pom.xml", "build.gradle", "build.gradle.kts"}:
        add(suggestions, "internal-project-java", "Java project path.")

    if "/workflows/" in lowered and suffix in {".yml", ".yaml"}:
        add(suggestions, "internal-github-actions", "GitHub Actions workflow path.")
    if "/actions/" in lowered and name in {"action.yml", "action.yaml"}:
        add(suggestions, "internal-github-action-composite", "Composite action metadata path.")
    if name.startswith("dockerfile") or "docker-compose" in name or "compose." in name:
        add(suggestions, "internal-docker", "Docker or Compose path.")
    if any(part in lowered for part in ("k8s/", "manifests/", "charts/")) and suffix in {
        ".yml",
        ".yaml",
    }:
        add(suggestions, "internal-kubernetes", "Kubernetes manifest path.")


def render_text(suggestions: dict[str, set[str]]) -> None:
    if not suggestions:
        print("No specific support skill suggested. Inspect files and scoped instructions first.")
        return

    for skill in sorted(suggestions):
        reasons = "; ".join(sorted(suggestions[skill]))
        print(f"- {skill}: {reasons}")


def render_json(suggestions: dict[str, set[str]]) -> None:
    payload = [
        {"skill": skill, "reasons": sorted(reasons)}
        for skill, reasons in sorted(suggestions.items())
    ]
    print(json.dumps(payload, indent=2))


def main() -> int:
    args = parse_args()
    suggestions: dict[str, set[str]] = {}

    for symptom in args.symptom:
        skill, reason = SYMPTOM_SKILLS[symptom]
        add(suggestions, skill, reason)
    for path_text in args.paths:
        suggest_for_path(path_text, suggestions)

    if args.format == "json":
        render_json(suggestions)
    else:
        render_text(suggestions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
