#!/usr/bin/env python3
"""Dispatch Copilot debug-log and prompt-export analyzers."""

from __future__ import annotations

import argparse

from tools.analyze_copilot_debug_log import debug_logs, prompt_exports


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Copilot debug-log and prompt-export files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompt_parser = subparsers.add_parser(
        "prompt-exports",
        help="Summarize Copilot prompt export JSON files.",
    )
    prompt_parser.add_argument("inputs", nargs="+", help="One or more Copilot prompt export JSON files.")
    prompt_parser.add_argument("--format", choices=("json", "markdown"), default="json")

    debug_parser = subparsers.add_parser(
        "debug-logs",
        help="Summarize Copilot debug-log or snapshot-export JSON files.",
    )
    debug_parser.add_argument("inputs", nargs="+", help="JSON debug-log or snapshot-export files.")
    debug_parser.add_argument("--format", choices=("json", "markdown"), default="json")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    delegated_args = [*args.inputs, "--format", args.format]
    if args.command == "prompt-exports":
        return prompt_exports.main(delegated_args)
    if args.command == "debug-logs":
        return debug_logs.main(delegated_args)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
