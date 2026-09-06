#!/usr/bin/env python3
"""Purpose: rebuild or verify the live Copilot inventory file.

Usage examples:
    ./.github/tools/run.sh build-inventory --root .
    ./.github/tools/run.sh build-inventory --root . --check
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))

from common.command import find_repo_root
from common.constants import INVENTORY_PATH
from common.files import read_text
from common.output import (
    log_error,
    log_info,
    log_success,
)

from inventory.inventory import build_inventory_markdown, write_inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild or verify .github/INVENTORY.md."
    )
    parser.add_argument(
        "--root", default=".", help="Repository root or any path inside it."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether the inventory is already up to date.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    expected_inventory = build_inventory_markdown(root)
    inventory_path = root / INVENTORY_PATH

    if args.check:
        current_inventory = read_text(inventory_path) if inventory_path.exists() else ""
        if current_inventory == expected_inventory:
            log_success("Inventory is already up to date.")
            return 0
        log_error("Inventory drift detected.")
        return 1

    log_info("Rebuilding .github/INVENTORY.md from filesystem state.")
    write_inventory(root)
    log_success("Inventory rebuilt successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
