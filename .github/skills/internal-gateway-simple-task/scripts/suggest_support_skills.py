#!/usr/bin/env python3
"""Suggest path and symptom-based support hints for internal-gateway-simple-task.

The script is advisory. It maps known paths and symptoms to the narrowest
currently proved repository owner. It should not expand one path into a
base-plus-depth stack or a referenced-skill chain when one owner already fits.
Absence from this helper is not evidence that a provider, runtime, or domain
is unsupported. Final selection still belongs to repository evidence,
path-to-skill routing, and explicit user-selected skills.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SYMPTOM_SKILLS = {
    "blocked": ("grill-me", "A blocker needs minimum clarification before continuing."),
    "bug": ("internal-debugging", "Bug or unexpected behavior needs reproduction."),
    "test-failure": ("internal-debugging", "A failing test needs root-cause diagnosis."),
    "build-failure": ("internal-debugging", "A failing build needs root-cause diagnosis."),
    "validator-drift": ("internal-debugging", "Validator drift needs a reproducible loop."),
    "unexpected": ("internal-debugging", "Unexpected output needs diagnosis before patching."),
    "missing-context": ("grill-me", "Missing context prevents starting the simple lane."),
    "tdd": ("internal-tdd", "Executable behavior should be delivered test-first."),
    "performance": ("internal-performance-optimization", "Performance is the primary measured concern."),
    "pr-readiness": ("internal-github-pr", "PR readiness, validity, mergeability, or completion needs PR lifecycle evidence."),
    "code-review": ("internal-code-review", "Line-level code review evidence is requested."),
    "systems-review": ("internal-high-level-review", "Cross-boundary or architecture review evidence is requested."),
    "completion-claim": ("superpowers-verification-before-completion", "Completion or readiness claim needs fresh validation evidence."),
    "no-findings": ("internal-code-review", "No-findings claim needs defect-first review evidence."),
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


def normalize_path_text(path_text: str) -> str:
    path = Path(path_text).expanduser()

    if path.is_absolute():
        repo_root = Path.cwd().resolve()

        try:
            return path.resolve().relative_to(repo_root).as_posix()
        except ValueError:
            return path.as_posix()

    return path.as_posix()


def is_script_path(lowered_path: str) -> bool:
    return lowered_path.startswith((".github/scripts/", "scripts/")) or "/scripts/" in lowered_path


def is_python_project_path(lowered_path: str) -> bool:
    return lowered_path.startswith(("src/", "app/", "services/")) or any(
        marker in lowered_path for marker in ("/src/", "/app/", "/services/")
    )


def is_node_project_path(lowered_path: str) -> bool:
    return lowered_path.startswith(("src/", "app/", "services/", "api/")) or any(
        marker in lowered_path
        for marker in ("/src/", "/app/", "/services/", "/api/")
    )


def is_java_project_path(lowered_path: str) -> bool:
    return lowered_path.startswith(("src/main/java/", "src/test/java/")) or any(
        marker in lowered_path for marker in ("/src/main/java/", "/src/test/java/")
    )


def suggest_for_path(path_text: str, suggestions: dict[str, set[str]]) -> None:
    normalized = normalize_path_text(path_text)
    lowered = normalized.lower()
    name = Path(normalized).name.lower()
    suffix = Path(lowered).suffix

    if normalized.startswith(".github/skills/internal-"):
        add(suggestions, "internal-skill-creator", "Repository-owned skill path.")
        return
    if normalized.startswith(".github/agents/internal-"):
        add(suggestions, "internal-agent-creator", "Repository-owned agent path.")
        return
    if name == "codeowners":
        add(suggestions, "internal-github-governance", "CODEOWNERS governance path.")
        return
    if name in {"makefile", "gnumakefile"} or suffix == ".mk":
        add(suggestions, "internal-makefile", "Makefile or make include path.")
        return
    if (
        name in {"azure-pipelines.yml", "azure-pipelines.yaml"}
        or name.startswith("azure-pipelines")
        or name.endswith(".pipeline.yml")
        or name.endswith(".pipeline.yaml")
    ):
        add(suggestions, "internal-azure-devops", "Azure DevOps pipeline path.")
        return
    if normalized in {".github/dependabot.yml", ".github/dependabot.yaml"}:
        add(suggestions, "awesome-copilot-dependabot", "Dependabot configuration path.")
        return
    if name in {
        "package-lock.json",
        "npm-shrinkwrap.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "bun.lock",
        "bun.lockb",
    }:
        add(suggestions, "internal-nodejs", "Node.js package-manager lockfile path.")
        return
    if name.startswith("dockerfile") or "docker-compose" in name or "compose." in name:
        add(suggestions, "internal-docker", "Docker or Compose path.")
        return
    if name == "chart.yaml":
        add(suggestions, "internal-kubernetes", "Helm chart metadata path.")
        return
    if "/workflows/" in lowered and suffix in {".yml", ".yaml"}:
        add(suggestions, "internal-github-actions", "GitHub Actions workflow path.")
        return
    if "/actions/" in lowered and name in {"action.yml", "action.yaml"}:
        add(suggestions, "internal-github-action-composite", "Composite action metadata path.")
        return
    if any(part in lowered for part in ("k8s/", "manifests/", "charts/")) and suffix in {
        ".yml",
        ".yaml",
    }:
        add(suggestions, "internal-kubernetes", "Kubernetes manifest path.")
        return
    if "lambda" in lowered and suffix in {".py", ".js", ".ts", ".tf"}:
        add(suggestions, "internal-aws-lambda", "Lambda-related file path.")
        return

    if suffix == ".py":
        if is_script_path(lowered):
            add(suggestions, "internal-script-python", "Python operational script path.")
        elif is_python_project_path(lowered):
            add(suggestions, "internal-project-python", "Python package or application path.")
        else:
            add(suggestions, "internal-python", "Python file path.")
    elif suffix == ".sh":
        if is_script_path(lowered) or name == "run.sh":
            add(suggestions, "internal-script-bash", "Bash script path.")
        else:
            add(suggestions, "internal-bash", "Shell or Bash file path.")
    elif suffix == ".tf":
        add(suggestions, "internal-terraform", "Terraform file path.")
    elif suffix == ".go" or name in {"go.mod", "go.sum"}:
        add(suggestions, "internal-go", "Go source or module path.")
    elif suffix in {".js", ".cjs", ".mjs", ".ts", ".tsx"} or name in {
        "package.json",
        "tsconfig.json",
    }:
        if name in {"package.json", "tsconfig.json"}:
            add(suggestions, "internal-nodejs", "JavaScript, Node.js, or TypeScript metadata path.")
        elif is_node_project_path(lowered):
            add(suggestions, "internal-project-nodejs", "Node.js or TypeScript project path.")
        else:
            add(suggestions, "internal-nodejs", "JavaScript, Node.js, or TypeScript path.")
    elif suffix == ".java":
        if is_java_project_path(lowered):
            add(suggestions, "internal-project-java", "Java project path.")
        else:
            add(suggestions, "internal-java", "Java source path.")
    elif name in {"pom.xml", "build.gradle", "build.gradle.kts"}:
        add(suggestions, "internal-java", "Java build metadata path.")
    elif suffix == ".md":
        add(suggestions, "internal-markdown", "Markdown file path.")
    elif suffix == ".json" and (
        lowered.startswith("config/")
        or "/config/" in lowered
        or any(
            part in lowered for part in ("authorizations/", "organization/", "src/", "data/")
        )
    ):
        add(suggestions, "internal-json", "Repository-owned JSON registry or data path.")

    elif suffix in {".yml", ".yaml"}:
        add(suggestions, "internal-yaml", "YAML file path.")


def render_text(suggestions: dict[str, set[str]]) -> None:
    if not suggestions:
        print(
            "No path or symptom-based support hint. Inspect files, domain skills, "
            "and explicit user-selected owners first."
        )
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
