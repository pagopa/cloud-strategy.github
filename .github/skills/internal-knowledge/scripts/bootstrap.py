#!/usr/bin/env python3
"""Bootstrap a portable knowledge map into a target repository."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from knowledge_core import discover_candidates, write_manifest


def emit_knowledge_map(repo_root: Path) -> Path:
    return write_manifest(repo_root, discover_candidates(repo_root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a portable knowledge map")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    repo_root.mkdir(parents=True, exist_ok=True)
    manifest_path = emit_knowledge_map(repo_root)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
