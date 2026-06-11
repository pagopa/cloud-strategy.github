#!/usr/bin/env python3
"""Minimal audit helper for internal-gateway-idea-brainstorming."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    bundle_dir = Path(__file__).resolve().parent.parent
    skill_text = (bundle_dir / "SKILL.md").read_text(encoding="utf-8")
    reference_text = (bundle_dir / "references" / "guided-decision-interview.md").read_text(
        encoding="utf-8"
    )
    runtime_text = (bundle_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
    markers = {
        "critical": "internal-gateway-critical-master" in skill_text,
        "planning": "internal-gateway-writing-plans" in skill_text,
        "stop_before_execution": "stop before execution" in skill_text,
        "plan_approval_gate": "Plan Approval Gate 3" in skill_text
        and "Plan Approval Gate 3" in reference_text,
        "handoff_gate_4": "Handoff Gate 4" in skill_text and "Handoff Gate 4" in reference_text,
        "ask_before_critical": "ask whether to continue" in skill_text
        and "ask whether to continue" in reference_text
        and "ask whether to continue" in runtime_text,
        "explicit_plan_approval": "go`/`ok`/`procedi" in skill_text
        and "go`/`ok`/`procedi" in reference_text
        and "go/ok/procedi" in runtime_text,
        "alias_mapping": "mini-plan" in skill_text
        and "mini-plan" in reference_text
        and "mini-plan" in runtime_text
        and "internal-gateway-simple-task" in runtime_text
        and "internal-gateway-execute-plans" in runtime_text,
    }
    print(json.dumps({"strict_ok": all(markers.values()), "markers": markers}, indent=2))
    return 0 if all(markers.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
