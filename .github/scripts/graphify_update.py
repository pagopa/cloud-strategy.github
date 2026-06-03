#!/usr/bin/env python3
"""Purpose: run Graphify on the repository root with governed corpus and metadata.

Usage examples:
  python3 ./.github/scripts/graphify_update.py --root .
  python3 ./.github/scripts/graphify_update.py --root . --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from lib.shared import find_repo_root, git_revision, log_error, log_info, log_success

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
GRAPHIFY_OUTPUT_DIR = Path("graphify-out")
GRAPHIFY_REFRESH_METADATA = GRAPHIFY_OUTPUT_DIR / ".internal-graphify-refresh.json"
GRAPHIFY_GRAPH_JSON = GRAPHIFY_OUTPUT_DIR / "graph.json"
GRAPHIFY_GRAPH_HTML = GRAPHIFY_OUTPUT_DIR / "graph.html"
GRAPHIFY_GRAPH_REPORT = GRAPHIFY_OUTPUT_DIR / "GRAPH_REPORT.md"
GRAPHIFY_REQUIRED_OUTPUTS = (GRAPHIFY_GRAPH_JSON, GRAPHIFY_GRAPH_REPORT)
GRAPHIFY_REBUILD_OUTPUTS = (GRAPHIFY_GRAPH_JSON, GRAPHIFY_GRAPH_HTML, GRAPHIFY_GRAPH_REPORT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Graphify on the repository root with governed corpus and metadata."
    )
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether the existing Graphify output is fresh and complete instead of refreshing.",
    )
    return parser.parse_args()


def is_allowlisted(relative_path: Path) -> bool:
    if relative_path.as_posix() in ALLOWED_FILES:
        return True

    if not relative_path.parts:
        return False

    return relative_path.parts[0] in ALLOWED_DIRECTORY_ROOTS


def list_governed_repo_files(root: Path) -> tuple[list[Path], int]:
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

    governed_paths: list[Path] = []
    for line in result.stdout.splitlines():
        relative_path = Path(line)
        source_path = root / relative_path
        if not is_allowlisted(relative_path):
            continue
        if not source_path.is_file():
            continue
        governed_paths.append(relative_path)

    governed_paths.sort(key=lambda path: path.as_posix())
    return governed_paths, 0


def compute_corpus_hash(root: Path, governed_paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for relative_path in governed_paths:
        file_path = root / relative_path
        file_digest = hashlib.sha256()
        with file_path.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(65536), b""):
                file_digest.update(chunk)
        digest.update(relative_path.as_posix().encode("utf-8"))
        digest.update(file_digest.digest())
    return digest.hexdigest()


def write_refresh_metadata(root: Path, governed_paths: list[Path]) -> None:
    metadata = {
        "commit": git_revision(root),
        "corpus_hash": compute_corpus_hash(root, governed_paths),
        "governed_files": [path.as_posix() for path in governed_paths],
        "source": "graphify_update.py",
    }
    metadata_path = root / GRAPHIFY_REFRESH_METADATA
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_refresh_metadata(root: Path) -> dict[str, object] | None:
    metadata_path = root / GRAPHIFY_REFRESH_METADATA
    if not metadata_path.is_file():
        return None
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def ensure_graphify_available() -> int:
    if shutil.which("graphify") is None:
        log_error("Missing required command: graphify")
        return 1
    return 0


def run_graphify_update(root: Path, *, force: bool = False) -> int:
    command = ["graphify", "update", "."]
    if force:
        command.append("--force")
    result = subprocess.run(
        command,
        cwd=root,
        check=False,
    )
    if result.returncode != 0:
        log_error("graphify update failed.")
        return result.returncode
    return 0


def verify_graphify_output_exists(root: Path) -> int:
    for expected_path in GRAPHIFY_REQUIRED_OUTPUTS:
        full_path = root / expected_path
        if not full_path.is_file():
            log_error(f"Expected Graphify output was not created: {expected_path.as_posix()}")
            return 1
    if not (root / GRAPHIFY_GRAPH_HTML).is_file():
        log_info(
            "Optional Graphify HTML visualization was not created; continuing with "
            "graph.json and GRAPH_REPORT.md only."
        )
    return 0


def remove_graphify_outputs(root: Path) -> None:
    for output_path in GRAPHIFY_REBUILD_OUTPUTS:
        full_path = root / output_path
        if full_path.exists():
            full_path.unlink()


def verify_graph_source_paths(root: Path, governed_paths: list[Path]) -> int:
    graph_path = root / GRAPHIFY_GRAPH_JSON
    if not graph_path.is_file():
        log_error("Graph JSON is missing; cannot verify source paths.")
        return 1

    try:
        graph_data = json.loads(graph_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log_error(f"Graph JSON is not valid JSON: {exc}")
        return 1

    governed_set = {path.as_posix() for path in governed_paths}
    ungoverned_paths: set[str] = set()

    def collect_paths(value: object, _seen: set[int]) -> None:
        if id(value) in _seen:
            return
        _seen.add(id(value))
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "source_file" and isinstance(item, str):
                    if item and item not in governed_set:
                        ungoverned_paths.add(item)
                collect_paths(item, _seen)
        elif isinstance(value, list):
            for item in value:
                collect_paths(item, _seen)

    collect_paths(graph_data, set())

    if ungoverned_paths:
        log_error(
            "Graph contains source paths outside the governed corpus: "
            + ", ".join(sorted(ungoverned_paths))
        )
        return 1

    return 0


def run_graphify_check(root: Path) -> int:
    log_info("Running Graphify freshness and completeness check.")

    exit_code = verify_graphify_output_exists(root)
    if exit_code != 0:
        return exit_code

    governed_paths, exit_code = list_governed_repo_files(root)
    if exit_code != 0:
        return exit_code

    if not governed_paths:
        log_error("No governed repository files were found for Graphify.")
        return 1

    exit_code = verify_graph_source_paths(root, governed_paths)
    if exit_code != 0:
        return exit_code

    metadata = read_refresh_metadata(root)
    if metadata is None:
        log_error("Graphify output exists but refresh metadata is missing.")
        return 1

    expected_commit = git_revision(root)
    actual_commit = metadata.get("commit")
    if actual_commit != expected_commit:
        log_error(
            f"Graphify output is stale: metadata commit {actual_commit!r} "
            f"does not match current HEAD {expected_commit!r}."
        )
        return 1

    expected_hash = compute_corpus_hash(root, governed_paths)
    actual_hash = metadata.get("corpus_hash")
    if actual_hash != expected_hash:
        log_error(
            "Graphify output is stale: corpus hash mismatch. "
            "The governed files or .graphifyignore have changed since the last refresh."
        )
        return 1

    log_success("Graphify output is fresh, complete, and within corpus boundary.")
    return 0


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))

    if args.check:
        exit_code = ensure_graphify_available()
        if exit_code != 0:
            return exit_code
        return run_graphify_check(root)

    governed_paths, exit_code = list_governed_repo_files(root)
    if exit_code != 0:
        return exit_code
    if not governed_paths:
        log_error("No governed repository files were found for Graphify.")
        return 1

    exit_code = ensure_graphify_available()
    if exit_code != 0:
        return exit_code

    root_output = root / GRAPHIFY_OUTPUT_DIR
    if root_output.exists():
        metadata_path = root / GRAPHIFY_REFRESH_METADATA
        if not metadata_path.is_file():
            log_error(
                f"A pre-existing {GRAPHIFY_OUTPUT_DIR.as_posix()}/ folder was found without "
                "internal refresh metadata. Refusing to overwrite. "
                "Please inspect, remove it manually if safe, then retry."
            )
            return 1

    log_info("Running graphify update .")
    exit_code = run_graphify_update(root)
    if exit_code != 0:
        return exit_code

    exit_code = verify_graphify_output_exists(root)
    if exit_code != 0:
        return exit_code

    exit_code = verify_graph_source_paths(root, governed_paths)
    if exit_code != 0:
        log_info(
            "Retrying graphify update with --force after clearing the previous graph snapshot "
            "to drop stale nodes after deletions or refactors."
        )
        remove_graphify_outputs(root)
        exit_code = run_graphify_update(root, force=True)
        if exit_code != 0:
            return exit_code

        exit_code = verify_graphify_output_exists(root)
        if exit_code != 0:
            return exit_code

        exit_code = verify_graph_source_paths(root, governed_paths)
        if exit_code != 0:
            return exit_code

    write_refresh_metadata(root, governed_paths)
    log_success(
        f"Graphify output is ready under {GRAPHIFY_OUTPUT_DIR.as_posix()}/ "
        f"and metadata was written to {GRAPHIFY_REFRESH_METADATA.as_posix()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
