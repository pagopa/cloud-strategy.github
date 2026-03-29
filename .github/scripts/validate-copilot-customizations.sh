#!/usr/bin/env python3
"""Validate core Copilot customization invariants for this repository.

Usage examples:
  python3 .github/scripts/validate-copilot-customizations.sh
  python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict
  python3 .github/scripts/validate-copilot-customizations.sh --report json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(".")
DEFAULT_SCOPE = "root"
DEFAULT_MODE = "strict"
SUPPORTED_SCOPES = {"root", "all"}
SUPPORTED_MODES = {"strict", "basic", "legacy-compatible"}
DEPRECATED_FRONTMATTER_KEYS = ("tools", "model", "color")


@dataclass
class ValidationReport:
    errors: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {"valid": self.valid, "errors": self.errors}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=DEFAULT_SCOPE)
    parser.add_argument("--mode", default=DEFAULT_MODE)
    parser.add_argument("--report", choices=("text", "json"), default="text")
    parser.add_argument("--report-file")
    return parser.parse_args()


def normalize_scope(scope: str) -> str:
    if scope not in SUPPORTED_SCOPES:
        raise ValueError(f"Unsupported scope: {scope}")
    return "root"


def normalize_mode(mode: str) -> str:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if mode == "legacy-compatible":
        return "basic"
    return mode


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_frontmatter_name(text: str) -> str:
    match = re.search(r"^name:\s*(.+)$", text, re.M)
    if not match:
        return ""
    return match.group(1).strip().strip("\"'")


def extract_inventory_paths() -> list[str]:
    inventory_paths: list[str] = []

    agents_path = REPO_ROOT / "AGENTS.md"
    if agents_path.exists():
        inside_inventory = False
        for raw_line in read_text(agents_path).splitlines():
            if raw_line.startswith("## Repository Inventory"):
                inside_inventory = True
                continue
            if not inside_inventory:
                continue
            if raw_line.startswith("- `") and raw_line.endswith("`"):
                inventory_paths.append(raw_line[3:-1])

    inventory_file = REPO_ROOT / ".github" / "INVENTORY.md"
    if inventory_file.exists():
        for raw_line in read_text(inventory_file).splitlines():
            if raw_line.startswith("- `") and raw_line.endswith("`"):
                inventory_paths.append(raw_line[3:-1])

    return sorted(set(inventory_paths))


def validate_named_resources(errors: list[str]) -> None:
    for skill_dir in sorted((REPO_ROOT / ".github" / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"Missing skill file: {skill_file}")
            continue

        text = read_text(skill_file)
        name = extract_frontmatter_name(text)
        if not name:
            errors.append(f"Missing frontmatter name: {skill_file}")
        elif name != skill_dir.name:
            errors.append(f"Skill name mismatch: {skill_dir.name} != {name}")

        for key in DEPRECATED_FRONTMATTER_KEYS:
            if re.search(rf"^{key}:\s*", text, re.M):
                errors.append(f"Deprecated frontmatter key `{key}:` found in {skill_file}")

    for prompt_file in sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")):
        text = read_text(prompt_file)
        name = extract_frontmatter_name(text)
        expected = prompt_file.name[: -len(".prompt.md")]
        if not name:
            errors.append(f"Missing frontmatter name: {prompt_file}")
        elif name != expected:
            errors.append(f"Prompt name mismatch: {expected} != {name}")

    for agent_file in sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")):
        text = read_text(agent_file)
        name = extract_frontmatter_name(text)
        expected = agent_file.name[: -len(".agent.md")]
        if not name:
            errors.append(f"Missing frontmatter name: {agent_file}")
        elif name != expected:
            errors.append(f"Agent name mismatch: {expected} != {name}")

        for key in DEPRECATED_FRONTMATTER_KEYS:
            if re.search(rf"^{key}:\s*", text, re.M):
                errors.append(f"Deprecated frontmatter key `{key}:` found in {agent_file}")


def validate_inventory(errors: list[str]) -> None:
    for relative in extract_inventory_paths():
        if not (REPO_ROOT / relative).exists():
            errors.append(f"Inventory path missing on disk: {relative}")


def validate_required_paths(errors: list[str]) -> None:
    required_paths = [
        Path("AGENTS.md"),
        Path(".github/copilot-instructions.md"),
        Path(".github/security-baseline.md"),
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"Missing required file: {path}")

    if Path(".github/AGENTS.md").exists():
        errors.append("Legacy .github/AGENTS.md exists; root AGENTS.md must be canonical.")


def build_report(scope: str, mode: str) -> ValidationReport:
    normalize_scope(scope)
    normalize_mode(mode)

    errors: list[str] = []
    validate_required_paths(errors)
    validate_named_resources(errors)
    validate_inventory(errors)
    return ValidationReport(errors=errors)


def emit_report(report: ValidationReport, fmt: str, report_file: str | None) -> None:
    if fmt == "json":
        payload = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
        if report_file:
            Path(report_file).write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return

    if report.valid:
        print("Validation passed.")
        if report_file:
            Path(report_file).write_text("Validation passed.\n", encoding="utf-8")
        return

    output = "\n".join(f"ERROR: {error}" for error in report.errors) + "\n"
    if report_file:
        Path(report_file).write_text(output, encoding="utf-8")
    sys.stderr.write(output)


def main() -> int:
    args = parse_args()

    try:
        report = build_report(args.scope, args.mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    emit_report(report, args.report, args.report_file)
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
