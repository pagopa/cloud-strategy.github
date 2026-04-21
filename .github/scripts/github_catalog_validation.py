#!/usr/bin/env python3
"""Purpose: simulate the _github-catalog-validation GitHub Actions workflow locally.

Usage examples:
  python3 ./.github/scripts/github_catalog_validation.py --root .
  python3 ./.github/scripts/github_catalog_validation.py --root . --skip-token-risks
  python3 ./.github/scripts/github_catalog_validation.py --root . --token-risks-only
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from lib.shared import find_repo_root, log_error, log_info, log_success, log_warn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate the _github-catalog-validation workflow locally."
    )
    parser.add_argument(
        "--root", default=".", help="Repository root or any path inside it."
    )
    parser.add_argument(
        "--skip-token-risks",
        action="store_true",
        help="Skip the optional token-risk scan.",
    )
    parser.add_argument(
        "--token-risks-only",
        action="store_true",
        help="Run only the optional token-risk scan.",
    )
    return parser.parse_args()


def run_make_target(root: Path, target: str, *, optional: bool) -> int:
    log_info(f"Running make {target}")
    result = subprocess.run(["make", target], cwd=root, check=False)
    if result.returncode == 0:
        log_success(f"Completed make {target}")
        return 0
    if optional:
        log_warn(
            "make "
            f"{target} reported findings; continuing to match "
            ".github/workflows/_github-catalog-validation.yml"
        )
        return 0
    log_error(f"make {target} failed.")
    return result.returncode


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    run_required_targets = not args.token_risks_only
    run_token_risks = args.token_risks_only or not args.skip_token_risks

    if run_required_targets:
        for target in (
            "catalog-lint",
            "test",
            "skill-lint",
            "catalog-check",
            "docs-lint",
        ):
            exit_code = run_make_target(root, target, optional=False)
            if exit_code != 0:
                return exit_code

    if run_token_risks:
        return run_make_target(root, "token-risks", optional=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
