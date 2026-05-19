#!/usr/bin/env python3
"""Measure estimated token cost for the internal-agent-creator skill bundle."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Finding:
    path: str
    severity: str
    code: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", default=".github/skills/internal-agent-creator")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--max-skill-md-tokens", type=int, default=4500)
    parser.add_argument("--max-reference-tokens", type=int, default=2000)
    parser.add_argument("--max-script-tokens", type=int, default=2600)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_dir = Path(args.skill_dir).resolve()
    findings: list[Finding] = []
    files: list[dict[str, object]] = []
    totals = {"loaded_docs": 0, "on_demand_docs": 0, "script_code": 0, "other": 0}

    for path in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
        if is_generated(path, skill_dir):
            continue
        rel = path.relative_to(skill_dir).as_posix()
        tokens = estimate_tokens(path)
        bucket = classify(rel)
        totals[bucket] += tokens
        files.append({"path": rel, "bucket": bucket, "estimated_tokens": tokens})

        if rel == "SKILL.md" and tokens > args.max_skill_md_tokens:
            findings.append(Finding(rel, "warning", "skill-md-large", f"SKILL.md is {tokens} estimated tokens."))
        if rel.startswith("references/") and tokens > args.max_reference_tokens:
            findings.append(Finding(rel, "warning", "reference-large", f"reference is {tokens} estimated tokens."))
        if rel.startswith("scripts/") and tokens > args.max_script_tokens:
            findings.append(Finding(rel, "warning", "script-large", f"script is {tokens} estimated tokens."))

    payload = {
        "files": files,
        "findings": [asdict(finding) for finding in findings],
        "totals": totals,
        "summary": {
            "file_count": len(files),
            "finding_count": len(findings),
            "total_estimated_tokens": sum(totals.values()),
        },
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        render_text(payload)

    return 1 if args.strict and findings else 0


def classify(relative_path: str) -> str:
    if relative_path == "SKILL.md":
        return "loaded_docs"
    if relative_path.startswith("references/") or relative_path == "agents/openai.yaml":
        return "on_demand_docs"
    if relative_path.startswith("scripts/"):
        return "script_code"
    return "other"


def is_generated(path: Path, skill_dir: Path) -> bool:
    relative_parts = path.relative_to(skill_dir).parts
    return "__pycache__" in relative_parts or path.suffix in {".pyc", ".pyo"}


def estimate_tokens(path: Path) -> int:
    return (len(path.read_bytes()) + 3) // 4


def render_text(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    totals = payload["totals"]
    print(
        "Skill token audit: "
        f"{summary['file_count']} files, "
        f"{summary['total_estimated_tokens']} estimated tokens."
    )
    print(
        "Buckets: "
        f"loaded_docs={totals['loaded_docs']}, "
        f"on_demand_docs={totals['on_demand_docs']}, "
        f"script_code={totals['script_code']}, "
        f"other={totals['other']}."
    )
    for finding in payload["findings"]:
        print(f"{finding['severity']}: {finding['path']} :: {finding['code']} :: {finding['message']}")


if __name__ == "__main__":
    raise SystemExit(main())
