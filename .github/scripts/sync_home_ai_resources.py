#!/usr/bin/env python3
"""Purpose: repo-local wrapper for the bundled home AI resource sync skill script.

Usage examples:
    python3 ./.github/scripts/sync_home_ai_resources.py sync --targets skills --format report
    python3 ./.github/scripts/sync_home_ai_resources.py apply --targets codex --create-missing-dirs --format report
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SKILL_SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills/local-agent-sync-install-ai-resources/scripts"
)
SKILL_CLI_PATH = SKILL_SCRIPT_DIR / "sync_home_ai_resources.py"


def load_skill_cli():
    inserted_path = False
    if SKILL_SCRIPT_DIR.as_posix() not in sys.path:
        sys.path.insert(0, SKILL_SCRIPT_DIR.as_posix())
        inserted_path = True
    try:
        spec = importlib.util.spec_from_file_location(
            "_local_agent_sync_home_ai_resources_cli",
            SKILL_CLI_PATH,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load skill CLI from {SKILL_CLI_PATH}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if inserted_path:
            sys.path.remove(SKILL_SCRIPT_DIR.as_posix())


SKILL_CLI = load_skill_cli()
parse_args = SKILL_CLI.parse_args


def main() -> int:
    return SKILL_CLI.run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
