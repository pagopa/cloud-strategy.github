#!/usr/bin/env python3
"""Command-line entrypoint for repository knowledge operating modes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bootstrap import emit_knowledge_map
from knowledge_core import (
    KnowledgeConfigError,
    audit_repository,
    check_repository,
    discover_candidates,
    impact_report,
    inventory_repository,
    load_knowledge_config,
    manifest_paths,
    normalize_target,
    write_manifest,
)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")


def print_report(report: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    for key, value in report.items():
        print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable repository knowledge tooling")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    for mode in ("audit", "bootstrap", "inventory", "check"):
        add_common_arguments(subparsers.add_parser(mode))

    impact_parser = subparsers.add_parser("impact")
    impact_parser.add_argument("--target", action="append", required=True)
    add_common_arguments(impact_parser)

    update_parser = subparsers.add_parser("update")
    update_selection = update_parser.add_mutually_exclusive_group(required=True)
    update_selection.add_argument("--target", action="append")
    update_selection.add_argument("--all", action="store_true")
    add_common_arguments(update_parser)
    return parser


def run_update(repo_root: Path, targets: list[str] | None, update_all: bool) -> tuple[int, dict[str, object]]:
    if update_all:
        return 0, {
            "mode": "update",
            "status": "approval-required",
            "resolved_targets": discover_candidates(repo_root),
            "next_action": "Re-supply approved paths with one --target argument per path.",
        }

    try:
        normalized_targets = [normalize_target(repo_root, target) for target in targets or []]
    except (PermissionError, ValueError) as error:
        return 2, {"mode": "update", "status": "blocked", "findings": [str(error)]}

    manifest_path = repo_root / "docs" / "knowledge-map.yaml"
    existing_paths = manifest_paths(manifest_path)
    write_manifest(repo_root, existing_paths + normalized_targets)
    return 0, {
        "mode": "update",
        "status": "updated",
        "updated_targets": sorted(dict.fromkeys(normalized_targets)),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()

    if args.mode in {"audit", "inventory", "check"}:
        if args.mode == "check" and args.config is None:
            print_report(
                {
                    "mode": "check",
                    "status": "blocked",
                    "findings": ["knowledge config is required"],
                },
                args.format,
            )
            return 2
        try:
            config = load_knowledge_config(repo_root, args.config)
        except KnowledgeConfigError as error:
            print_report(
                {"mode": args.mode, "status": "blocked", "findings": [str(error)]},
                args.format,
            )
            return 2
        if args.mode == "audit":
            exit_code, report = 0, audit_repository(repo_root, config)
        elif args.mode == "inventory":
            exit_code, report = 0, inventory_repository(repo_root, config)
        else:
            report = check_repository(repo_root, config)
            exit_code = 0 if report.get("status") == "passed" else 1
    elif args.mode == "impact":
        exit_code, report = 0, impact_report(repo_root, args.target)
    elif args.mode == "bootstrap":
        manifest_path = emit_knowledge_map(repo_root)
        exit_code, report = 0, {
            "mode": "bootstrap",
            "status": "created",
            "artifacts": [manifest_path.relative_to(repo_root).as_posix()],
        }
    else:
        exit_code, report = run_update(repo_root, args.target, args.all)

    print_report(report, args.format)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
