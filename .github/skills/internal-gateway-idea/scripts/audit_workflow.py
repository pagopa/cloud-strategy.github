#!/usr/bin/env python3
"""Audit the internal-gateway-idea workflow gate contract."""

from __future__ import annotations

import json
from pathlib import Path


def contains_all(text: str, markers: list[str]) -> bool:
    return all(marker in text for marker in markers)


def main() -> int:
    bundle_dir = Path(__file__).resolve().parent.parent
    skill_text = (bundle_dir / "SKILL.md").read_text(encoding="utf-8")
    workflow_text = (bundle_dir / "references" / "workflow.md").read_text(encoding="utf-8")
    runtime_text = (bundle_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")

    shared_markers = [
        "Specialization Checkpoint: gated",
        "Idea Gate 0",
        "visible numbered question block",
        "Assumption Challenge Gate",
        "Alternative discovery",
        "Critical Challenge Gate",
        "embedded critique does not satisfy Critical Challenge Gate",
        "Spec vs plan decision",
        "internal-gateway-writing-plans",
        "Stop before implementation execution",
    ]
    workflow_only_markers = [
        "flowchart TD",
        "Approval Rules",
        "Coexistence Rule",
    ]
    runtime_only_markers = [
        "$internal-gateway-idea",
        "$superpowers-brainstorming",
        "$internal-gateway-writing-plans",
        "do not implement",
    ]

    markers = {
        "skill_shared_markers": contains_all(skill_text, shared_markers),
        "workflow_shared_markers": contains_all(workflow_text, shared_markers),
        "runtime_core_markers": contains_all(runtime_text, runtime_only_markers)
        and contains_all(
            runtime_text,
            [
                "Specialization Checkpoint: gated",
                "Idea Gate 0",
                "Critical Challenge Gate",
                "spec-vs-plan decision",
            ],
        ),
        "workflow_mermaid_and_rules": contains_all(workflow_text, workflow_only_markers),
        "coexistence_boundary": "internal-gateway-idea-brainstorming" in skill_text
        and "internal-gateway-idea-brainstorming" in workflow_text
        and "internal-gateway-idea-brainstorming" in runtime_text,
        "approval_is_gate_local": "active visible gate" in skill_text
        and "active visible gate" in workflow_text
        and "active visible gate" in runtime_text,
        "evidence_cannot_replace_questions": "evidence cannot replace Idea Gate 0"
        in skill_text
        and "evidence cannot replace Idea Gate 0" in workflow_text
        and "evidence cannot replace Idea Gate 0" in runtime_text,
        "skipped_gate_recovery": "first skipped mandatory gate" in skill_text
        and "first skipped mandatory gate" in workflow_text
        and "first skipped mandatory gate" in runtime_text,
        "stop_before_execution": "Stop before implementation execution" in workflow_text
        and "Stop after the delegated writing outcome" in skill_text
        and "Stop after the writing outcome" in runtime_text,
    }
    payload = {"strict_ok": all(markers.values()), "markers": markers}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["strict_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
