#!/usr/bin/env python3
"""Purpose: stage an allowlisted repository corpus and run Graphify manually.

Usage examples:
  python3 ./.github/scripts/graphify_update.py --root .
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from lib.shared import find_repo_root, log_error, log_info, log_success

ALLOWED_DIRECTORY_ROOTS = frozenset({".github", "docs"})
ALLOWED_FILES = frozenset(
    {
        "AGENTS.md",
        "INTERNAL_CONTRACT.md",
        "LESSONS_LEARNED.md",
        "Makefile",
        ".pre-commit-config.yaml",
    }
)
GRAPHIFY_WORKSPACE_RELATIVE = Path("tmp/.graphify")
GRAPHIFY_STAGING_RELATIVE = GRAPHIFY_WORKSPACE_RELATIVE / "graphify"
GRAPHIFY_OUTPUT_RELATIVE = GRAPHIFY_STAGING_RELATIVE / "graphify-out/graph.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage the allowlisted repository corpus and run Graphify manually."
    )
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    return parser.parse_args()


def is_allowlisted(relative_path: Path) -> bool:
    if relative_path.as_posix() in ALLOWED_FILES:
        return True

    if not relative_path.parts:
        return False

    return relative_path.parts[0] in ALLOWED_DIRECTORY_ROOTS


def list_allowlisted_repo_files(root: Path) -> tuple[list[Path], int]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        log_error("git ls-files failed while building the Graphify corpus.")
        return [], result.returncode

    allowlisted_paths: list[Path] = []
    for line in result.stdout.splitlines():
        relative_path = Path(line)
        source_path = root / relative_path
        if not is_allowlisted(relative_path):
            continue
        if not source_path.is_file():
            continue
        allowlisted_paths.append(relative_path)

    allowlisted_paths.sort(key=lambda path: path.as_posix())
    return allowlisted_paths, 0


def rebuild_staging_corpus(root: Path, relative_paths: list[Path]) -> Path:
    staging_root = root / GRAPHIFY_STAGING_RELATIVE
    if staging_root.exists():
        shutil.rmtree(staging_root)
    staging_root.mkdir(parents=True, exist_ok=True)

    for relative_path in relative_paths:
        source_path = root / relative_path
        destination_path = staging_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

    return staging_root


def initialize_staging_git_repo(staging_root: Path) -> int:
    for command in (["git", "init", "--quiet"], ["git", "add", "--all"]):
        result = subprocess.run(command, cwd=staging_root, check=False)
        if result.returncode == 0:
            continue
        log_error(f"{' '.join(command)} failed while preparing the staged Graphify corpus.")
        return result.returncode

    return 0


def cleanup_unexpected_root_output(root: Path, *, existed_before: bool) -> None:
    root_output = root / "graphify-out"
    if existed_before or not root_output.exists():
        return

    if root_output.is_dir():
        shutil.rmtree(root_output)
    else:
        root_output.unlink()

    log_info("Removed unexpected root graphify-out/ artifact created during Graphify refresh.")


def ensure_graphify_available() -> int:
    if shutil.which("graphify") is None:
        log_error("Missing required command: graphify")
        return 1

    return 0


def run_graphify_update(root: Path) -> int:

    result = subprocess.run(
        ["graphify", "update", GRAPHIFY_STAGING_RELATIVE.as_posix()],
        cwd=root,
        check=False,
    )
    if result.returncode != 0:
        log_error("graphify update failed.")
        return result.returncode

    graph_path = root / GRAPHIFY_OUTPUT_RELATIVE
    if not graph_path.is_file():
        log_error(
            "Expected Graphify output was not created: "
            f"{GRAPHIFY_OUTPUT_RELATIVE.as_posix()}"
        )
        return 1

    log_success(f"Graphify output is ready at {GRAPHIFY_OUTPUT_RELATIVE.as_posix()}.")
    return 0


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    root_output_existed = (root / "graphify-out").exists()
    allowlisted_paths, exit_code = list_allowlisted_repo_files(root)
    if exit_code != 0:
        return exit_code
    if not allowlisted_paths:
        log_error("No allowlisted repository files were found for Graphify.")
        return 1
    exit_code = ensure_graphify_available()
    if exit_code != 0:
        return exit_code

    log_info(f"Preparing Graphify corpus under {GRAPHIFY_STAGING_RELATIVE.as_posix()}.")
    staging_root = rebuild_staging_corpus(root, allowlisted_paths)
    log_info(f"Staged {len(allowlisted_paths)} repository files for Graphify.")
    log_info("Initializing a temporary Git index for the staged Graphify corpus.")
    exit_code = initialize_staging_git_repo(staging_root)
    if exit_code != 0:
        return exit_code
    log_info(f"Running graphify update {GRAPHIFY_STAGING_RELATIVE.as_posix()}")
    exit_code = run_graphify_update(root)
    cleanup_unexpected_root_output(root, existed_before=root_output_existed)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
