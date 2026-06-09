#!/usr/bin/env python3
"""Minimal audit helper for internal-gateway-idea-brainstorming."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    bundle_dir = Path(__file__).resolve().parent.parent
    skill_text = (bundle_dir / "SKILL.md").read_text(encoding="utf-8")
    markers = {
        "critical": "internal-gateway-critical-master" in skill_text,
        "planning": "internal-writing-plans" in skill_text,
        "stop_before_execution": "stop before execution" in skill_text,
    }
    print(json.dumps({"strict_ok": all(markers.values()), "markers": markers}, indent=2))
    return 0 if all(markers.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
