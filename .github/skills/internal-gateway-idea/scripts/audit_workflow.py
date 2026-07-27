#!/usr/bin/env python3
"""Audit the internal-gateway-idea workflow gate contract."""

from __future__ import annotations

import json
from pathlib import Path


def contains_all(text: str, markers: list[str]) -> bool:
    return all(marker in text for marker in markers)


def contains_in_order(text: str, markers: list[str]) -> bool:
    try:
        positions = [text.index(marker) for marker in markers]
    except ValueError:
        return False
    return positions == sorted(positions)


def runtime_prompt_text(runtime_source: str) -> str:
    """Return the de-indented prompt body from the YAML runtime surface."""
    _, prompt_source = runtime_source.split("default_prompt:", 1)
    prompt_lines = prompt_source.splitlines()[1:]
    return "\n".join(
        line[4:] if line.startswith("    ") else line for line in prompt_lines
    )


MANDATORY_SEQUENCE = [
    "Specialization Checkpoint: gated",
    "Idea Gate 0",
    "External Research Checkpoint",
    "Assumption Challenge Gate",
    "Alternative discovery",
    "Critical Challenge Gate",
    "Critical resolution loop",
    "Automatic plan handoff",
    "Stop before implementation execution",
]

RUNTIME_SEQUENCE = [
    "Specialization Checkpoint: gated",
    "Idea Gate 0",
    "External Research Checkpoint",
    "Assumption Challenge Gate",
    "Alternative discovery",
    "Critical Challenge Gate",
    "Critical resolution loop",
    "Automatic plan handoff",
    "Stop before implementation execution",
]


def main() -> int:
    bundle_dir = Path(__file__).resolve().parent.parent
    skill_text = (bundle_dir / "SKILL.md").read_text(encoding="utf-8")
    workflow_text = (bundle_dir / "references" / "workflow.md").read_text(encoding="utf-8")
    runtime_source = (bundle_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
    runtime_text = runtime_prompt_text(runtime_source)

    shared_markers = [
        "Specialization Checkpoint: gated",
        "Idea Gate 0",
        "compact user-facing decision card",
        "Assumption Challenge Gate",
        "Alternative discovery",
        "Critical Challenge Gate",
        "embedded critique does not satisfy Critical Challenge Gate",
        "Critical resolution loop",
        "Automatic plan handoff",
        "internal-gateway-writing-plans",
        "Stop before implementation execution",
    ]
    critical_routing_markers = [
        "accepted",
        "revise-design",
        "reopen-analysis",
        "needs-clarification",
        "every material objection raised during the current critical pass is closed or explicitly routed",
        "load `/grill-me`",
        "one or more numbered clarification sessions",
        "newly surfaced elements",
        "material change",
        "relevant earlier approval gate",
        "rerun `Critical Challenge Gate` directly",
    ]
    handoff_card = """🚀 **Scrittura del piano avviata**
✅ La critica si è conclusa senza obiezioni materiali aperte.
🛠️ `/internal-gateway-writing-plans` sta preparando il piano di implementazione."""
    critical_mermaid_markers = [
        "M -- accepted --> Q1[Automatic plan handoff]",
        "M -- revise-design --> J",
        "M -- reopen-analysis --> D",
        "M -- needs-clarification --> R[Run one or more /grill-me sessions]",
        "R --> R1{Did clarification materially change an accepted decision?}",
        "R1 -- yes --> R2[Return to relevant earlier approval gate]",
        "R1 -- no --> L",
    ]
    chat_projection_markers = [
        "compact user-facing decision card",
        "internal workflow state",
        "🎯",
        "🧭",
        "🛠️",
        "🧪",
        "⚠️",
        "✅",
        "💡",
        "✈️",
    ]
    workflow_only_markers = [
        "flowchart TD",
        "Approval Rules",
        "Routing Stability Rule",
    ]
    research_markers = [
        "mattpocock-research",
        "External Research Checkpoint",
        "tmp/research/",
        "on-demand",
        "local evidence is insufficient",
        "feasibility, approach, constraints, or risk",
        "one bounded research question",
        "one Markdown report",
        "decision-relevant conclusions",
        "do not start a second research pass automatically",
    ]
    runtime_only_markers = [
        "/internal-gateway-idea",
        "/superpowers-brainstorming",
        "/internal-gateway-writing-plans",
        "do not implement",
        "agent filename, frontmatter name, and workflow aligned",
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
                "Critical resolution loop",
                "Automatic plan handoff",
            ],
        ),
        "skill_gate_sequence": contains_in_order(skill_text, MANDATORY_SEQUENCE),
        "workflow_gate_sequence": contains_in_order(workflow_text, MANDATORY_SEQUENCE),
        "runtime_gate_sequence": contains_in_order(runtime_text, RUNTIME_SEQUENCE),
        "runtime_research_checkpoint": contains_all(
            runtime_text,
            [
                "External Research Checkpoint",
                "mattpocock-research",
                "on-demand",
            ],
        ),
        "local_fast_lane_documented": ".github/skills/internal-gateway-idea/scripts/audit_workflow.py" in skill_text
        and ".github/skills/internal-gateway-idea/scripts/audit_workflow.py" in workflow_text,
        "workflow_mermaid_and_rules": contains_all(workflow_text, workflow_only_markers),
        "skill_research_escalation": contains_all(skill_text, research_markers),
        "workflow_research_escalation": contains_all(
            workflow_text, research_markers
        ),
        "canonical_alignment": "agent filename, frontmatter name, and workflow aligned" in skill_text
        and "agent filename, frontmatter name, and workflow aligned" in workflow_text
        and "agent filename, frontmatter name, and workflow aligned" in runtime_text,
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
        "compact_chat_projection": all(
            contains_all(text, chat_projection_markers)
            for text in (skill_text, workflow_text, runtime_text)
        ),
        "critical_routing": all(
            contains_all(text, critical_routing_markers)
            for text in (skill_text, workflow_text, runtime_text)
        ),
        "handoff_card": all(
            handoff_card in text for text in (skill_text, workflow_text, runtime_text)
        ),
        "skill_exclusion_removed": "## When not to use" not in skill_text,
        "critical_mermaid_routing": contains_all(
            workflow_text, critical_mermaid_markers
        ),
        "spec_choice_removed": all(
            "Spec vs plan decision" not in text
            and "Decision: spec first" not in text
            and "Approval request" not in text
            for text in (skill_text, workflow_text, runtime_text)
        ),
        "automatic_plan_handoff": "M -- accepted --> Q1[Automatic plan handoff]"
        in workflow_text
        and "Q1A --> Q2[Load /internal-gateway-writing-plans]" in workflow_text,
        "repeatable_grill_me_loop": "M -- needs-clarification --> R[Run one or more /grill-me sessions]"
        in workflow_text
        and "R1 -- no --> L" in workflow_text,
        "writing_gateway_is_plan_only": "implementation-plan writing" in skill_text
        and "retained spec or implementation-plan writing" not in skill_text
        and "retained spec or implementation-plan writing" not in workflow_text
        and "retained spec or implementation-plan writing" not in runtime_text,
    }
    payload = {"strict_ok": all(markers.values()), "markers": markers}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["strict_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
