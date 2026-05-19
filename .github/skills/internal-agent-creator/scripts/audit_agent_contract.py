#!/usr/bin/env python3
"""Report repository-owned agent contract shape without modifying files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


LEGACY_SKILL_HEADINGS = (
    "## Mandatory Engine Skills",
    "## Optional Support Skills",
    "## Preferred/Optional Skills",
)


@dataclass
class Finding:
    path: str
    severity: str
    code: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--max-agent-tokens", type=int, default=1800)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    agents_dir = root / ".github" / "agents"
    findings: list[Finding] = []
    agents: list[dict[str, object]] = []

    for path in sorted(agents_dir.glob("*.agent.md")):
        if not path.name.startswith(("internal-", "local-")):
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root).as_posix()
        frontmatter = parse_frontmatter(text)
        body = body_text(text)
        core_skills = section_bullets(body, "Core Skill")
        legacy_headings = [heading for heading in LEGACY_SKILL_HEADINGS if heading in body]
        est_tokens = estimate_tokens(text)

        agents.append(
            {
                "path": relative,
                "name": frontmatter.get("name"),
                "estimated_tokens": est_tokens,
                "core_skills": core_skills,
                "legacy_skill_headings": legacy_headings,
            }
        )

        expected_name = path.name.removesuffix(".agent.md")
        if frontmatter.get("name") != expected_name:
            findings.append(Finding(relative, "error", "name-mismatch", f"name should be {expected_name}."))
        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.startswith("Use this agent when"):
            findings.append(Finding(relative, "warning", "weak-description", "description should start with 'Use this agent when'."))
        tools = frontmatter.get("tools")
        if not isinstance(tools, list) or not tools:
            findings.append(Finding(relative, "warning", "missing-tools", "repo-owned agents should declare a role-shaped tools list."))
        if len(core_skills) > 1:
            findings.append(Finding(relative, "error", "multiple-core-skills", "## Core Skill must list exactly one skill."))
        if core_skills:
            skill_path = root / ".github" / "skills" / core_skills[0] / "SKILL.md"
            if not skill_path.exists():
                findings.append(Finding(relative, "error", "missing-core-skill", f"core skill does not exist: {core_skills[0]}"))
        for heading in legacy_headings:
            findings.append(Finding(relative, "info", "legacy-skill-heading", f"legacy heading present for benchmark or future migration: {heading}"))
        if est_tokens > args.max_agent_tokens:
            findings.append(Finding(relative, "warning", "large-agent", f"estimated token count is {est_tokens}."))

    payload = {
        "agents": agents,
        "findings": [asdict(finding) for finding in findings],
        "summary": {
            "agent_count": len(agents),
            "finding_count": len(findings),
            "legacy_agent_count": sum(1 for agent in agents if agent["legacy_skill_headings"]),
        },
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        render_text(payload)

    has_actionable = any(finding.severity in {"error", "warning"} for finding in findings)
    return 1 if args.strict and has_actionable else 0


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        return {}
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    data: dict[str, object] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if key_match:
            current_key = key_match.group(1)
            data[current_key] = parse_scalar_or_list(key_match.group(2).strip())
        elif current_key and line.strip().startswith("- "):
            values = data.setdefault(current_key, [])
            if isinstance(values, list):
                values.append(line.strip()[2:].strip().strip("'\""))
    return data


def parse_scalar_or_list(value: str) -> object:
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
    return value.strip("'\"")


def body_text(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def section_bullets(body: str, heading: str) -> list[str]:
    marker = f"## {heading}"
    if marker not in body:
        return []
    section = body.split(marker, 1)[1].split("\n## ", 1)[0]
    bullets: list[str] = []
    for line in section.splitlines():
        match = re.match(r"^-\s+`?([^`\n]+?)`?\s*$", line.strip())
        if match:
            bullets.append(match.group(1).strip())
    return bullets


def estimate_tokens(text: str) -> int:
    return (len(text.encode("utf-8")) + 3) // 4


def render_text(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    print(
        "Agent audit: "
        f"{summary['agent_count']} agents, "
        f"{summary['finding_count']} findings, "
        f"{summary['legacy_agent_count']} legacy skill-heading agents."
    )
    for finding in payload["findings"]:
        print(f"{finding['severity']}: {finding['path']} :: {finding['code']} :: {finding['message']}")


if __name__ == "__main__":
    raise SystemExit(main())
