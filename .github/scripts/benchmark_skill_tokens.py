#!/usr/bin/env python3
"""Deterministic static benchmark for skill routing scenario proxies.

Measures explicit on-demand context proxies for representative scenarios.
Does not claim exact GitHub runtime loading or billed savings.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ESTIMATED_TOKEN_BYTES = 4

SCENARIOS = [
    ("Python generic", "tools/check.py", "internal-python"),
    ("Python script", ".github/scripts/tool.py", "internal-python-script"),
    ("Python project", "src/app.py", "internal-python-project"),
    ("Bash generic", "bin/check.sh", "internal-bash"),
    ("Bash script", "scripts/demo.sh", "internal-bash-script"),
    ("Node metadata", "package.json", "internal-nodejs"),
    ("Node project", "src/index.ts", "internal-nodejs-project"),
    ("Java metadata", "pom.xml", "internal-java"),
    ("Java project", "src/main/java/App.java", "internal-java-project"),
    ("YAML generic", "config/app.yaml", "internal-yaml"),
    ("Terraform", "infra/main.tf", "internal-terraform"),
]

CHAIN_RISK_PATTERNS = [
    re.compile(r"[Ll]oad `internal-[^`]+` (?:first |only )?for the shared"),
    re.compile(r"[Ll]oad `internal-[^`]+` (?:first |only )?when"),
    re.compile(r"[Rr]eference `internal-[^`]+` (?:first |only )?for"),
    re.compile(r"[Uu]se `internal-[^`]+` (?:first |only )?for the shared"),
    re.compile(r"[Tt]reat `internal-[^`]+` as (?:the )?base"),
    re.compile(r"[Ll]oad the base skill"),
    re.compile(r"[Ll]oad the shared (?:Python|JavaScript|Bash|Java) baseline"),
]


def detect_chain_risks(skill_name: str, root: Path) -> list[str]:
    skill_md = root / ".github" / "skills" / skill_name / "SKILL.md"
    if not skill_md.exists():
        return []

    text = skill_md.read_text(encoding="utf-8")
    risks: list[str] = []
    for pattern in CHAIN_RISK_PATTERNS:
        for match in pattern.finditer(text):
            # Extract the referenced skill name from backticks
            inner = re.search(r"`internal-[^`]+`", match.group(0))
            if inner:
                referenced = inner.group(0).strip("`")
                if referenced != skill_name and referenced not in risks:
                    risks.append(referenced)
    return risks


def estimate_tokens(path: Path) -> int:
    if not path.exists():
        return 0
    return (len(path.read_bytes()) + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES


def estimate_skill_tokens(skill_name: str, root: Path) -> int:
    skill_md = root / ".github" / "skills" / skill_name / "SKILL.md"
    return estimate_tokens(skill_md)


def estimate_bundle_tokens(skill_name: str, root: Path) -> int:
    skill_dir = root / ".github" / "skills" / skill_name
    if not skill_dir.exists():
        return 0
    total = 0
    for path in skill_dir.rglob("*"):
        if path.is_file():
            total += len(path.read_bytes())
    return (total + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES


def build_scenario_report(root: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for scenario_name, _path_hint, expected_owner in SCENARIOS:
        skill_md = root / ".github" / "skills" / expected_owner / "SKILL.md"
        skill_tokens = estimate_tokens(skill_md)
        bundle_tokens = estimate_bundle_tokens(expected_owner, root)

        chain_risks = detect_chain_risks(expected_owner, root)
        chain_tokens = 0
        for chained_skill in chain_risks:
            chain_tokens += estimate_skill_tokens(chained_skill, root)

        scenario_proxy = skill_tokens + chain_tokens

        reports.append({
            "scenario": scenario_name,
            "expected_owner": expected_owner,
            "skill_tokens": skill_tokens,
            "bundle_tokens": bundle_tokens,
            "chain_tokens": chain_tokens,
            "scenario_proxy": scenario_proxy,
            "chain_risks": chain_risks,
        })
    return reports


GATEWAY_SKILL = "internal-gateway-operational-flow"

GATEWAY_REQUIRED_CONTEXT_SCENARIOS: dict[str, list[str]] = {
    "Direct execute": [GATEWAY_SKILL],
    "Define Gate 0": [GATEWAY_SKILL, "grill-me", "internal-gateway-operational-flow"],
    "Define idea and critical": [
        GATEWAY_SKILL, "grill-me", "internal-gateway-idea-brainstorming",
        "internal-gateway-critical-master",
    ],
    "Plan handoff": [GATEWAY_SKILL, "internal-writing-plans", "internal-agent-support-next-step"],
    "Approved apply-plan": [GATEWAY_SKILL, "internal-executing-plans"],
    "Review verdict": [
        GATEWAY_SKILL, "internal-code-review", "internal-high-level-review",
        "internal-gateway-critical-master",
    ],
}

GATEWAY_OUTPUT_FIELD_SCENARIOS: dict[str, list[str]] = {
    "Terminal direct execute": ["result", "evidence", "risk"],
    "Define checkpoint": ["gate", "brief", "validation", "risk", "checkpoint"],
    "Plan checkpoint": ["decision", "validation", "risk", "checkpoint"],
    "Non-terminal apply-plan stop": ["state", "continuation", "user_action", "evidence", "next_step"],
    "Review verdict": ["finding", "confidence", "evidence_gap", "risk", "route"],
}


def build_gateway_report(root: Path) -> dict[str, Any]:
    core_bytes = len((root / ".github" / "skills" / GATEWAY_SKILL / "SKILL.md").read_bytes())
    bundle_dir = root / ".github" / "skills" / GATEWAY_SKILL
    bundle_bytes = sum(
        len(p.read_bytes()) for p in bundle_dir.rglob("*") if p.is_file()
    )

    context_scenarios: list[dict[str, Any]] = []
    for name, skills in GATEWAY_REQUIRED_CONTEXT_SCENARIOS.items():
        total_bytes = 0
        for skill_name in skills:
            skill_path = root / ".github" / "skills" / skill_name / "SKILL.md"
            if skill_path.exists():
                total_bytes += len(skill_path.read_bytes())
        context_scenarios.append({
            "scenario": name,
            "required_skills": skills,
            "bytes": total_bytes,
            "estimated_tokens": (total_bytes + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES,
        })

    output_scenarios: list[dict[str, Any]] = []
    for name, fields in GATEWAY_OUTPUT_FIELD_SCENARIOS.items():
        field_bytes = sum(len(f.encode("utf-8")) for f in fields)
        output_scenarios.append({
            "scenario": name,
            "fields": fields,
            "field_count": len(fields),
            "field_bytes": field_bytes,
        })

    return {
        "core_bytes": core_bytes,
        "core_estimated_tokens": (core_bytes + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES,
        "bundle_bytes": bundle_bytes,
        "bundle_estimated_tokens": (bundle_bytes + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES,
        "required_context_scenarios": context_scenarios,
        "output_field_scenarios": output_scenarios,
    }


def build_description_report(root: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    skills_root = root / ".github" / "skills"
    for skill_dir in sorted(skills_root.glob("*/SKILL.md")):
        skill_name = skill_dir.parent.name
        text = skill_dir.read_text(encoding="utf-8")
        # Extract frontmatter description
        description = ""
        if text.startswith("---"):
            try:
                _, frontmatter_text, _ = text.split("---", 2)
                for line in frontmatter_text.splitlines():
                    if line.strip().startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                        break
            except ValueError:
                pass

        desc_chars = len(description)
        desc_tokens = (desc_chars + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES

        reports.append({
            "skill": skill_name,
            "description_chars": desc_chars,
            "description_tokens": desc_tokens,
            "description": description[:100] + "..." if len(description) > 100 else description,
        })
    return reports


def main() -> int:
    root = Path.cwd()
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])

    scenario_reports = build_scenario_report(root)
    description_reports = build_description_report(root)
    gateway_report = build_gateway_report(root)

    description_reports.sort(key=lambda r: r["description_tokens"], reverse=True)

    output = {
        "scenarios": scenario_reports,
        "descriptions": description_reports,
        "gateway": gateway_report,
        "summary": {
            "total_scenarios": len(scenario_reports),
            "total_skills_measured": len(description_reports),
            "highest_description_tokens": description_reports[0]["description_tokens"] if description_reports else 0,
            "highest_scenario_proxy": max((r["scenario_proxy"] for r in scenario_reports), default=0),
            "gateway_core_bytes": gateway_report["core_bytes"],
            "gateway_bundle_bytes": gateway_report["bundle_bytes"],
        },
    }

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
