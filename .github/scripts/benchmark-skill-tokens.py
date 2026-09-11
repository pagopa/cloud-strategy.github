#!/usr/bin/env python3
"""Deterministic static benchmark for skill routing scenario proxies.

Measures explicit on-demand context proxies for representative scenarios.
Does not claim exact GitHub runtime loading or billed savings.
"""

from __future__ import annotations

import argparse
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
]

ANTON_CORE_SKILL = "antonbabenko-terraform-skill"

TERRAFORM_SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario": "hcl-only",
        "primary_owner": "internal-tf",
        "delegated_owner": None,
        "delegated_core_owner": None,
        "loaded_local_references": ["references/common-mistakes.md"],
        "forbidden_local_references": [
            "references/existing-infrastructure-adoption.md",
            "references/operational-validation.md",
        ],
    },
    {
        "scenario": "tfvars-json-only",
        "primary_owner": "internal-tf",
        "delegated_owner": None,
        "delegated_core_owner": None,
        "loaded_local_references": ["references/structure-standard.md"],
        "forbidden_local_references": [
            "references/existing-infrastructure-adoption.md",
            "references/operational-validation.md",
        ],
    },
    {
        "scenario": "mixed-adoption",
        "primary_owner": "internal-terraform",
        "delegated_owner": "internal-tf",
        "delegated_core_owner": ANTON_CORE_SKILL,
        "loaded_local_references": [
            "references/existing-infrastructure-adoption.md",
            "references/structure-standard.md",
        ],
        "forbidden_local_references": ["references/operational-validation.md"],
    },
    {
        "scenario": "native-test",
        "primary_owner": "internal-terraform",
        "delegated_owner": None,
        "delegated_core_owner": ANTON_CORE_SKILL,
        "loaded_local_references": ["references/operational-validation.md"],
        "forbidden_local_references": [
            "references/existing-infrastructure-adoption.md"
        ],
    },
    {
        "scenario": "state-or-drift",
        "primary_owner": "internal-terraform",
        "delegated_owner": None,
        "delegated_core_owner": ANTON_CORE_SKILL,
        "loaded_local_references": ["references/operational-validation.md"],
        "forbidden_local_references": [
            "references/existing-infrastructure-adoption.md"
        ],
    },
    {
        "scenario": "module-architecture",
        "primary_owner": "internal-terraform",
        "delegated_owner": None,
        "delegated_core_owner": ANTON_CORE_SKILL,
        "loaded_local_references": [],
        "forbidden_local_references": [
            "references/existing-infrastructure-adoption.md",
            "references/operational-validation.md",
        ],
    },
    {
        "scenario": "ci-or-provider-operation",
        "primary_owner": "internal-terraform",
        "delegated_owner": None,
        "delegated_core_owner": ANTON_CORE_SKILL,
        "loaded_local_references": ["references/operational-validation.md"],
        "forbidden_local_references": [
            "references/existing-infrastructure-adoption.md"
        ],
    },
    {
        "scenario": "ambiguous-adoption-identity",
        "primary_owner": "internal-terraform",
        "delegated_owner": None,
        "delegated_core_owner": ANTON_CORE_SKILL,
        "loaded_local_references": ["references/existing-infrastructure-adoption.md"],
        "forbidden_local_references": [],
    },
)

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

        reports.append(
            {
                "scenario": scenario_name,
                "expected_owner": expected_owner,
                "skill_tokens": skill_tokens,
                "bundle_tokens": bundle_tokens,
                "chain_tokens": chain_tokens,
                "scenario_proxy": scenario_proxy,
                "chain_risks": chain_risks,
            }
        )
    return reports


def _estimate_reference_tokens(
    reference: str,
    owners: list[str],
    root: Path,
) -> int:
    for owner in owners:
        reference_path = root / ".github" / "skills" / owner / reference
        if reference_path.is_file():
            return estimate_tokens(reference_path)
    return 0


def build_terraform_scenario_report(root: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for scenario in TERRAFORM_SCENARIOS:
        primary_owner = scenario["primary_owner"]
        delegated_owner = scenario["delegated_owner"]
        owners = [primary_owner]
        if delegated_owner:
            owners.append(delegated_owner)

        local_skill_tokens = estimate_skill_tokens(primary_owner, root)
        conditional_reference_tokens = sum(
            _estimate_reference_tokens(reference, owners, root)
            for reference in scenario["loaded_local_references"]
        )
        delegated_core_owner = scenario["delegated_core_owner"]
        delegated_core_tokens = (
            estimate_skill_tokens(delegated_core_owner, root)
            if delegated_core_owner
            else 0
        )

        reports.append(
            {
                "scenario": scenario["scenario"],
                "primary_owner": primary_owner,
                "delegated_owner": delegated_owner,
                "delegated_core_owner": delegated_core_owner,
                "loaded_local_references": list(scenario["loaded_local_references"]),
                "forbidden_local_references": list(
                    scenario["forbidden_local_references"]
                ),
                "local_skill_tokens": local_skill_tokens,
                "conditional_reference_tokens": conditional_reference_tokens,
                "delegated_core_tokens": delegated_core_tokens,
                "scenario_proxy_tokens": (
                    local_skill_tokens
                    + conditional_reference_tokens
                    + delegated_core_tokens
                ),
            }
        )
    return reports


GATEWAY_SKILL = "internal-gateway-idea"
REVIEW_COUNTERCHECK_SKILL = "internal-gateway-critical-master"

GATEWAY_REQUIRED_CONTEXT_SCENARIOS: dict[str, list[str]] = {
    "Direct execute": [GATEWAY_SKILL, "internal-gateway-simple-task"],
    "Define Gate 0": [GATEWAY_SKILL, "grill-me"],
    "Define idea and critical": [
        GATEWAY_SKILL,
        "grill-me",
        "internal-gateway-critical-master",
    ],
    "Plan handoff": [GATEWAY_SKILL, "internal-gateway-writing-plans"],
    "Approved apply-plan": [GATEWAY_SKILL, "internal-gateway-execute-plans"],
    "Review counter-check": [
        REVIEW_COUNTERCHECK_SKILL,
    ],
}

IDEA_GATEWAY_SKILL = "internal-gateway-idea"

IDEA_GATEWAY_SCENARIOS: dict[str, list[str]] = {
    "Idea core entry": [IDEA_GATEWAY_SKILL],
    "Interview support": [IDEA_GATEWAY_SKILL, "grill-me"],
    "Mandatory critical pass": [
        IDEA_GATEWAY_SKILL,
        "internal-gateway-critical-master",
    ],
    "Visible handoff": [IDEA_GATEWAY_SKILL],
}

GATEWAY_OUTPUT_FIELD_SCENARIOS: dict[str, list[str]] = {
    "Terminal direct execute": ["result", "evidence", "risk"],
    "Define checkpoint": ["gate", "brief", "validation", "risk", "checkpoint"],
    "Plan checkpoint": ["decision", "validation", "risk", "checkpoint"],
    "Non-terminal apply-plan stop": [
        "state",
        "continuation",
        "user_action",
        "evidence",
        "next_step",
    ],
    "Review verdict": ["finding", "confidence", "evidence_gap", "risk", "route"],
}


def build_gateway_report(root: Path) -> dict[str, Any]:
    core_bytes = len(
        (root / ".github" / "skills" / GATEWAY_SKILL / "SKILL.md").read_bytes()
    )
    bundle_dir = root / ".github" / "skills" / GATEWAY_SKILL
    bundle_bytes = sum(
        len(p.read_bytes()) for p in bundle_dir.rglob("*") if p.is_file()
    )

    context_scenarios: list[dict[str, Any]] = []
    for name, skills in GATEWAY_REQUIRED_CONTEXT_SCENARIOS.items():
        total_bytes = 0
        deduped = list(dict.fromkeys(skills))
        for skill_name in deduped:
            skill_path = root / ".github" / "skills" / skill_name / "SKILL.md"
            if skill_path.exists():
                total_bytes += len(skill_path.read_bytes())
        context_scenarios.append(
            {
                "scenario": name,
                "required_skills": deduped,
                "bytes": total_bytes,
                "estimated_tokens": (total_bytes + ESTIMATED_TOKEN_BYTES - 1)
                // ESTIMATED_TOKEN_BYTES,
            }
        )

    output_scenarios: list[dict[str, Any]] = []
    for name, fields in GATEWAY_OUTPUT_FIELD_SCENARIOS.items():
        field_bytes = sum(len(f.encode("utf-8")) for f in fields)
        output_scenarios.append(
            {
                "scenario": name,
                "fields": fields,
                "field_count": len(fields),
                "field_bytes": field_bytes,
            }
        )

    return {
        "core_bytes": core_bytes,
        "core_estimated_tokens": (core_bytes + ESTIMATED_TOKEN_BYTES - 1)
        // ESTIMATED_TOKEN_BYTES,
        "bundle_bytes": bundle_bytes,
        "bundle_estimated_tokens": (bundle_bytes + ESTIMATED_TOKEN_BYTES - 1)
        // ESTIMATED_TOKEN_BYTES,
        "required_context_scenarios": context_scenarios,
        "output_field_scenarios": output_scenarios,
    }


def build_idea_gateway_report(root: Path) -> dict[str, Any]:
    core_path = root / ".github" / "skills" / IDEA_GATEWAY_SKILL / "SKILL.md"
    core_bytes = len(core_path.read_bytes()) if core_path.exists() else 0
    bundle_dir = root / ".github" / "skills" / IDEA_GATEWAY_SKILL
    bundle_bytes = (
        sum(len(p.read_bytes()) for p in bundle_dir.rglob("*") if p.is_file())
        if bundle_dir.exists()
        else 0
    )

    context_scenarios: list[dict[str, Any]] = []
    for name, skills in IDEA_GATEWAY_SCENARIOS.items():
        total_bytes = 0
        deduped = list(dict.fromkeys(skills))
        for skill_name in deduped:
            skill_path = root / ".github" / "skills" / skill_name / "SKILL.md"
            if skill_path.exists():
                total_bytes += len(skill_path.read_bytes())
        context_scenarios.append(
            {
                "scenario": name,
                "required_skills": deduped,
                "bytes": total_bytes,
                "estimated_tokens": (total_bytes + ESTIMATED_TOKEN_BYTES - 1)
                // ESTIMATED_TOKEN_BYTES,
            }
        )

    return {
        "core_bytes": core_bytes,
        "core_estimated_tokens": (core_bytes + ESTIMATED_TOKEN_BYTES - 1)
        // ESTIMATED_TOKEN_BYTES,
        "bundle_bytes": bundle_bytes,
        "bundle_estimated_tokens": (bundle_bytes + ESTIMATED_TOKEN_BYTES - 1)
        // ESTIMATED_TOKEN_BYTES,
        "context_scenarios": context_scenarios,
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

        reports.append(
            {
                "skill": skill_name,
                "description_chars": desc_chars,
                "description_tokens": desc_tokens,
                "description": description[:100] + "..."
                if len(description) > 100
                else description,
            }
        )
    return reports


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic static benchmark for skill routing scenario proxies.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository root path (defaults to current directory).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root)

    scenario_reports = build_scenario_report(root)
    terraform_scenario_reports = build_terraform_scenario_report(root)
    description_reports = build_description_report(root)
    gateway_report = build_gateway_report(root)
    idea_gateway_report = build_idea_gateway_report(root)

    description_reports.sort(key=lambda r: r["description_tokens"], reverse=True)

    output = {
        "measurement_note": (
            "This is a static proxy; it does not prove runtime loading, "
            "cache behavior, or billed-token savings."
        ),
        "scenarios": scenario_reports,
        "terraform_scenarios": terraform_scenario_reports,
        "descriptions": description_reports,
        "gateway": gateway_report,
        "idea_gateway": idea_gateway_report,
        "summary": {
            "total_scenarios": len(scenario_reports) + len(terraform_scenario_reports),
            "total_skills_measured": len(description_reports),
            "highest_description_tokens": description_reports[0]["description_tokens"]
            if description_reports
            else 0,
            "highest_scenario_proxy": max(
                [
                    *(r["scenario_proxy"] for r in scenario_reports),
                    *(r["scenario_proxy_tokens"] for r in terraform_scenario_reports),
                ],
                default=0,
            ),
            "gateway_core_bytes": gateway_report["core_bytes"],
            "gateway_bundle_bytes": gateway_report["bundle_bytes"],
        },
    }

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
