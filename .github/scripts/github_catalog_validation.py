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

from lib.shared import (
    find_repo_root,
    log_error,
    log_info,
    log_success,
    log_warn,
    render_json,
)


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
    parser.add_argument(
        "--format",
        choices=["text", "json", "compact"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional path for full command output when --format is json or compact.",
    )
    return parser.parse_args()


def _tail_lines(text: str, max_lines: int = 8) -> list[str]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    return lines[-max_lines:]


def run_make_target(
    root: Path,
    target: str,
    *,
    optional: bool,
    output_format: str,
    log_file: Path | None,
) -> tuple[int, dict[str, object]]:
    log_info(f"Running make {target}")
    if output_format == "text":
        result = subprocess.run(["make", target], cwd=root, check=False)
        details = {
            "target": target,
            "optional": optional,
            "returncode": result.returncode,
            "output_tail": [],
        }
    else:
        result = subprocess.run(
            ["make", target],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = "\n".join(part for part in (stdout.strip(), stderr.strip()) if part)
        if log_file is not None:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8") as handle:
                handle.write(f"$ make {target}\n")
                handle.write(combined)
                handle.write("\n\n")
        details = {
            "target": target,
            "optional": optional,
            "returncode": result.returncode,
            "output_tail": _tail_lines(combined),
        }

    if result.returncode == 0:
        log_success(f"Completed make {target}")
        return 0, details
    if optional:
        log_warn(
            "make "
            f"{target} reported findings; continuing to match "
            ".github/workflows/_github-catalog-validation.yml"
        )
        return 0, details
    log_error(f"make {target} failed.")
    return result.returncode, details


def emit_compact_summary(
    *,
    root: Path,
    results: list[dict[str, object]],
    log_file: Path | None,
    exit_code: int,
    output_format: str,
) -> None:
    failed_required = [item for item in results if item["returncode"] != 0 and not item["optional"]]
    warned_optional = [item for item in results if item["returncode"] != 0 and item["optional"]]
    payload = {
        "mode": "github-catalog-validation",
        "status": "ok" if exit_code == 0 else "failed",
        "repo_root": root.as_posix(),
        "targets_run": len(results),
        "failed_required": [item["target"] for item in failed_required],
        "optional_warnings": [item["target"] for item in warned_optional],
        "target_results": [
            {
                "target": item["target"],
                "optional": item["optional"],
                "returncode": item["returncode"],
                "output_tail": item["output_tail"],
            }
            for item in results
        ],
    }
    if log_file is not None:
        payload["full_output_log"] = log_file.as_posix()
    if output_format == "json":
        print(render_json(payload))
        return

    compact_payload = {
        "mode": payload["mode"],
        "status": payload["status"],
        "failed_required": payload["failed_required"],
        "optional_warnings": payload["optional_warnings"],
        "targets_run": payload["targets_run"],
        "next_action": (
            "Investigate the first failed required target and inspect full_output_log."
            if exit_code != 0
            else "Validation completed; continue with task-specific follow-up."
        ),
    }
    if log_file is not None:
        compact_payload["full_output_log"] = log_file.as_posix()
    print(render_json(compact_payload))


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    output_format = getattr(args, "format", "text")
    log_file = None
    if output_format in {"json", "compact"}:
        log_file = Path(args.log_file) if args.log_file else root / "tmp/github-catalog-validation.latest.log"
        if log_file.exists():
            log_file.unlink()

    run_required_targets = not args.token_risks_only
    run_token_risks = args.token_risks_only or not args.skip_token_risks
    results: list[dict[str, object]] = []
    exit_code = 0

    if run_required_targets:
        for target in (
            "catalog-lint",
            "test",
            "skill-lint",
            "catalog-check",
            "docs-lint",
        ):
            exit_code, details = run_make_target(
                root,
                target,
                optional=False,
                output_format=output_format,
                log_file=log_file,
            )
            results.append(details)
            if exit_code != 0:
                break

    if exit_code == 0 and run_token_risks:
        exit_code, details = run_make_target(
            root,
            "token-risks",
            optional=True,
            output_format=output_format,
            log_file=log_file,
        )
        results.append(details)

    if output_format in {"json", "compact"}:
        emit_compact_summary(
            root=root,
            results=results,
            log_file=log_file,
            exit_code=exit_code,
            output_format=output_format,
        )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
