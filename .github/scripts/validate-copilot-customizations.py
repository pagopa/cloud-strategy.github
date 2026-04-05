#!/usr/bin/env python3
"""Validate core Copilot customization invariants for this repository.

Usage examples:
  python3 .github/scripts/validate-copilot-customizations.py
  python3 .github/scripts/validate-copilot-customizations.py --scope root --mode strict
  python3 .github/scripts/validate-copilot-customizations.py --report json
"""

from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(".")
DEFAULT_SCOPE = "root"
DEFAULT_MODE = "strict"
SUPPORTED_SCOPES = {"root", "all"}
SUPPORTED_MODES = {"strict", "basic", "legacy-compatible"}
RETIRED_FRONTMATTER_KEYS = ("infer", "color")
DEPRECATED_AGENT_SECTION_HEADINGS = ("## Primary Skill Stack",)
AGENT_SKILL_SECTION_HEADINGS = ("## Preferred/Optional Skills",)
INTERNAL_SYNC_CONTROL_CENTER_AGENT = Path(".github/agents/internal-sync-control-center.agent.md")
INTERNAL_SYNC_CONTROL_CENTER_REQUIRED_SKILLS = {
    "internal-skill-management",
    "internal-copilot-audit",
    "internal-agent-development",
    "internal-copilot-docs-research",
    "internal-agents-md-bridge",
}
LEGACY_SKILL_IDENTIFIER = "internal-skill-development"
OBRA_SOURCE_OF_TRUTH_PATH = Path(".github/obra-superpowers-source-of-truth.json")
OBRA_MANAGED_RESOURCE_SECTION = "### `obra/superpowers`"
OBRA_GOVERNANCE_REFERENCE_PATHS = (
    Path("AGENTS.md"),
    Path(".github/copilot-instructions.md"),
)
INTERNAL_CODE_REVIEW_REFERENCE_PATHS = (
    Path(".github/skills/internal-code-review/references/anti-patterns-python.md"),
    Path(".github/skills/internal-code-review/references/anti-patterns-bash.md"),
    Path(".github/skills/internal-code-review/references/anti-patterns-terraform.md"),
    Path(".github/skills/internal-code-review/references/anti-patterns-java.md"),
    Path(".github/skills/internal-code-review/references/anti-patterns-nodejs.md"),
)
OPERATION_COMPLETION_REPORT_SECTION = "## Operation Completion Report"
COMPLETION_REPORT_CONTRACT_SECTION = "## Completion Report Contract"
COMPLETION_REPORT_CATEGORY_HEADINGS = (
    "### ✅ Outcome",
    "### 🤖 Agents",
    "### 📘 Instructions",
    "### 🧩 Skills",
)
COMPLETION_REPORT_UNUSED_REASON = (
    "If a category was not used, explicitly say so and explain why."
)
AGENTS_COMPLETION_REPORT_POINTER = (
    "Completion-report details live in `.github/copilot-instructions.md`"
)
SYNC_AGENT_COMPLETION_REPORT_PATHS = (
    Path(".github/agents/internal-sync-control-center.agent.md"),
    Path(".github/agents/internal-sync-global-copilot-configs-into-repo.agent.md"),
)


@dataclass
class ValidationReport:
    errors: list[str]
    warnings: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings}


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


def extract_frontmatter_apply_to(text: str) -> list[str]:
    match = re.search(r"^applyTo:\s*(.+)$", text, re.M)
    if not match:
        return []

    raw_value = match.group(1).strip().strip("\"'")
    return [pattern.strip() for pattern in raw_value.split(",") if pattern.strip()]


def has_frontmatter_key(text: str, key: str) -> bool:
    return re.search(rf"^{re.escape(key)}:\s*", text, re.M) is not None


def extract_markdown_h2_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    inside_section = False
    collected: list[str] = []

    for line in lines:
        if re.match(r"^##\s+", line):
            if line.strip() == heading:
                inside_section = True
                collected = []
                continue
            if inside_section:
                break

        if inside_section:
            collected.append(line)

    if not inside_section:
        return None

    return "\n".join(collected).strip()


def extract_markdown_h3_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    inside_section = False
    collected: list[str] = []

    for line in lines:
        if re.match(r"^###\s+", line):
            if line.strip() == heading:
                inside_section = True
                collected = []
                continue
            if inside_section:
                break

        if inside_section:
            collected.append(line)

    if not inside_section:
        return None

    return "\n".join(collected).strip()


def extract_agent_skill_guidance(text: str) -> list[str] | None:
    section = None
    for heading in AGENT_SKILL_SECTION_HEADINGS:
        section = extract_markdown_h2_section(text, heading)
        if section is not None:
            break
    if section is None:
        return None

    declared_skills: list[str] = []
    for raw_line in section.splitlines():
        match = re.fullmatch(r"\s*-\s+`([^`]+)`\s*", raw_line)
        if match:
            declared_skills.append(match.group(1))

    return declared_skills


def extract_skill_usage_contract(text: str) -> list[str] | None:
    section = extract_markdown_h2_section(text, "## Skill Usage Contract")
    if section is None:
        return None

    declared_skills: list[str] = []
    for raw_line in section.splitlines():
        match = re.fullmatch(r"\s*-\s+`([^`]+)`:\s+.+", raw_line)
        if match:
            declared_skills.append(match.group(1))

    return declared_skills


def extract_managed_skill_mappings(text: str, resource_heading: str) -> list[tuple[str, str]] | None:
    section = extract_markdown_h3_section(text, resource_heading)
    if section is None:
        return None

    inside_managed_skills = False
    mappings: list[tuple[str, str]] = []

    for raw_line in section.splitlines():
        stripped = raw_line.strip()
        if stripped == "Managed skills:":
            inside_managed_skills = True
            continue

        if not inside_managed_skills:
            continue

        match = re.fullmatch(r"-\s+`([^`]+)`\s+->\s+`([^`]+)`", stripped)
        if match:
            mappings.append((match.group(1), match.group(2)))

    return mappings


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


def local_catalog_inventory_paths() -> set[str]:
    paths: set[str] = set()
    paths.update(
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in instruction_files()
    )
    paths.update(
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md"))
    )
    paths.update(
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md"))
    )
    paths.update(
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md"))
    )
    return paths


def has_declared_inventory() -> bool:
    agents_path = REPO_ROOT / "AGENTS.md"
    if agents_path.exists() and "## Repository Inventory" in read_text(agents_path):
        return True
    return (REPO_ROOT / ".github" / "INVENTORY.md").exists()


def instruction_files() -> list[Path]:
    instructions_dir = REPO_ROOT / ".github" / "instructions"
    if not instructions_dir.exists():
        return []
    return sorted(instructions_dir.glob("*.instructions.md"))


def count_file_lines(path: Path) -> int:
    return len(read_text(path).splitlines())


def instruction_load_samples() -> list[str]:
    return [
        ".github/workflows/ci.yml",
        ".github/actions/example/action.yml",
        "Dockerfile",
        "compose.yaml",
        "infra/main.tf",
        "infra/eng-azure-platform/main.tf",
        "infra/eng-aws-platform/main.tf",
        "infra/eng-gcp-platform/main.tf",
    ]


def matching_instructions_for_path(sample_path: str) -> list[tuple[str, int]]:
    sample = PurePosixPath(sample_path)
    matches: list[tuple[str, int]] = []

    for instruction_path in instruction_files():
        patterns = extract_frontmatter_apply_to(read_text(instruction_path))
        if any(sample.match(pattern) for pattern in patterns):
            matches.append((instruction_path.name, count_file_lines(instruction_path)))

    return matches


def build_instruction_load_warnings() -> list[str]:
    warnings: list[str] = []

    for sample_path in instruction_load_samples():
        matches = matching_instructions_for_path(sample_path)
        if len(matches) < 2:
            continue

        total_lines = sum(line_count for _name, line_count in matches)
        if total_lines < 300:
            continue

        joined_names = ", ".join(name for name, _line_count in matches)
        warnings.append(
            "Instruction load hotspot for "
            f"`{sample_path}`: {len(matches)} instructions / {total_lines} lines "
            f"({joined_names})"
        )

    return warnings


def validate_named_resources(errors: list[str]) -> None:
    skill_names: set[str] = set()

    for skill_dir in sorted((REPO_ROOT / ".github" / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"Missing skill file: {skill_file}")
            continue

        skill_names.add(skill_dir.name)
        text = read_text(skill_file)
        name = extract_frontmatter_name(text)
        if not name:
            errors.append(f"Missing frontmatter name: {skill_file}")
        elif name != skill_dir.name:
            errors.append(f"Skill name mismatch: {skill_dir.name} != {name}")

        for key in RETIRED_FRONTMATTER_KEYS:
            if re.search(rf"^{key}:\s*", text, re.M):
                errors.append(f"Retired frontmatter key `{key}:` found in {skill_file}")

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
        is_internal_agent = expected.startswith("internal-")
        if not name:
            errors.append(f"Missing frontmatter name: {agent_file}")
        elif is_internal_agent and name != expected:
            errors.append(f"Agent name mismatch: {expected} != {name}")

        if not is_internal_agent:
            continue

        if not has_frontmatter_key(text, "tools"):
            errors.append(f"Missing required frontmatter key `tools:` in {agent_file}")

        for key in RETIRED_FRONTMATTER_KEYS:
            if re.search(rf"^{key}:\s*", text, re.M):
                errors.append(f"Retired frontmatter key `{key}:` found in {agent_file}")

        for heading in DEPRECATED_AGENT_SECTION_HEADINGS:
            if re.search(rf"^{re.escape(heading)}\s*$", text, re.M):
                errors.append(f"Deprecated agent section `{heading}` found in {agent_file}")

        listed_skills = extract_agent_skill_guidance(text)
        if listed_skills is None:
            continue

        if not listed_skills:
            errors.append(f"`## Preferred/Optional Skills` must list at least one skill: {agent_file}")
            continue

        for skill_name in listed_skills:
            if skill_name not in skill_names:
                errors.append(
                    f"Unknown preferred or optional skill `{skill_name}` referenced in {agent_file}"
                )


def validate_inventory(errors: list[str]) -> None:
    inventory_paths = set(extract_inventory_paths())

    for relative in sorted(inventory_paths):
        if not (REPO_ROOT / relative).exists():
            errors.append(f"Inventory path missing on disk: {relative}")

    if not has_declared_inventory():
        return

    for relative in sorted(local_catalog_inventory_paths() - inventory_paths):
        errors.append(f"Inventory path missing from declared inventory: {relative}")


def validate_repo_profile_references(errors: list[str]) -> None:
    repo_profiles_path = REPO_ROOT / ".github" / "repo-profiles.yml"
    if not repo_profiles_path.exists():
        return

    for raw_line in read_text(repo_profiles_path).splitlines():
        stripped = raw_line.split("#", 1)[0].strip()
        if not stripped.startswith("- "):
            continue

        candidate = stripped[2:].strip().strip("\"'")
        if not candidate.startswith(("instructions/", "prompts/", "skills/")):
            continue

        absolute_path = REPO_ROOT / ".github" / candidate
        if not absolute_path.exists():
            errors.append(f"Repo profile path missing on disk: .github/{candidate}")


def should_validate_obra_source_of_truth() -> bool:
    if (REPO_ROOT / OBRA_SOURCE_OF_TRUTH_PATH).exists():
        return True

    if (REPO_ROOT / INTERNAL_SYNC_CONTROL_CENTER_AGENT).exists():
        return True

    return any((REPO_ROOT / ".github" / "skills").glob("obra-*/SKILL.md"))


def validate_obra_source_of_truth(errors: list[str]) -> None:
    if not should_validate_obra_source_of_truth():
        return

    source_of_truth_path = REPO_ROOT / OBRA_SOURCE_OF_TRUTH_PATH
    if not source_of_truth_path.exists():
        errors.append(f"Missing OBRA source-of-truth file: {OBRA_SOURCE_OF_TRUTH_PATH}")
        return

    try:
        source_of_truth = json.loads(read_text(source_of_truth_path))
    except json.JSONDecodeError as error:
        errors.append(f"Invalid JSON in {OBRA_SOURCE_OF_TRUTH_PATH}: {error}")
        return

    if not isinstance(source_of_truth, dict):
        errors.append(f"Invalid OBRA source-of-truth payload in {OBRA_SOURCE_OF_TRUTH_PATH}")
        return

    if not isinstance(source_of_truth.get("source_repository"), str) or not source_of_truth.get(
        "source_repository"
    ):
        errors.append(
            f"Missing `source_repository` string in {OBRA_SOURCE_OF_TRUTH_PATH}"
        )

    if not isinstance(source_of_truth.get("source_ref"), str) or not source_of_truth.get(
        "source_ref"
    ):
        errors.append(f"Missing `source_ref` string in {OBRA_SOURCE_OF_TRUTH_PATH}")

    raw_managed_skills = source_of_truth.get("managed_skills")
    if not isinstance(raw_managed_skills, list) or not raw_managed_skills:
        errors.append(f"Missing `managed_skills` list in {OBRA_SOURCE_OF_TRUTH_PATH}")
        return

    expected_mappings: set[tuple[str, str]] = set()
    for entry in raw_managed_skills:
        if not isinstance(entry, dict):
            errors.append(f"Invalid managed skill entry in {OBRA_SOURCE_OF_TRUTH_PATH}: {entry!r}")
            continue

        upstream = entry.get("upstream")
        local = entry.get("local")
        if not isinstance(upstream, str) or not upstream or not isinstance(local, str) or not local:
            errors.append(
                "Managed skill entries must contain non-empty `upstream` and `local` strings in "
                f"{OBRA_SOURCE_OF_TRUTH_PATH}"
            )
            continue

        expected_mappings.add((upstream, local))

    expected_local_skills = {local for _upstream, local in expected_mappings}
    actual_local_skills = {
        path.parent.name
        for path in sorted((REPO_ROOT / ".github" / "skills").glob("obra-*/SKILL.md"))
    }

    for skill_name in sorted(expected_local_skills - actual_local_skills):
        errors.append(
            f"OBRA source-of-truth skill missing on disk: {skill_name} ({OBRA_SOURCE_OF_TRUTH_PATH})"
        )

    for skill_name in sorted(actual_local_skills - expected_local_skills):
        errors.append(
            f"Unexpected local OBRA skill outside source-of-truth: {skill_name} ({OBRA_SOURCE_OF_TRUTH_PATH})"
        )

    control_center_path = REPO_ROOT / INTERNAL_SYNC_CONTROL_CENTER_AGENT
    if not control_center_path.exists():
        return

    managed_mappings = extract_managed_skill_mappings(read_text(control_center_path), OBRA_MANAGED_RESOURCE_SECTION)
    if managed_mappings is None:
        errors.append(
            f"Missing `{OBRA_MANAGED_RESOURCE_SECTION}` section: {INTERNAL_SYNC_CONTROL_CENTER_AGENT}"
        )
        return

    managed_mapping_set = set(managed_mappings)
    for upstream, local in sorted(expected_mappings - managed_mapping_set):
        errors.append(
            "OBRA managed skill mapping missing from "
            f"{INTERNAL_SYNC_CONTROL_CENTER_AGENT}: `{upstream}` -> `{local}`"
        )

    for upstream, local in sorted(managed_mapping_set - expected_mappings):
        errors.append(
            "Unexpected OBRA managed skill mapping in "
            f"{INTERNAL_SYNC_CONTROL_CENTER_AGENT}: `{upstream}` -> `{local}`"
        )


def validate_governance_obra_skill_references(errors: list[str]) -> None:
    available_obra_skills = {
        path.parent.name
        for path in sorted((REPO_ROOT / ".github" / "skills").glob("obra-*/SKILL.md"))
    }
    if not available_obra_skills:
        return

    for relative_path in OBRA_GOVERNANCE_REFERENCE_PATHS:
        absolute_path = REPO_ROOT / relative_path
        if not absolute_path.exists():
            continue

        for skill_name in sorted(set(re.findall(r"`(obra-[a-z0-9-]+)`", read_text(absolute_path)))):
            if skill_name not in available_obra_skills:
                errors.append(f"Unknown obra skill `{skill_name}` referenced in {relative_path}")


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


def validate_internal_sync_control_center_contract(errors: list[str]) -> None:
    agent_path = REPO_ROOT / INTERNAL_SYNC_CONTROL_CENTER_AGENT
    if not agent_path.exists():
        return

    text = read_text(agent_path)
    listed_skills = extract_agent_skill_guidance(text) or []
    skill_usage_contract = extract_skill_usage_contract(text)

    if skill_usage_contract is None:
        errors.append(
            f"Missing `## Skill Usage Contract` section: {INTERNAL_SYNC_CONTROL_CENTER_AGENT}"
        )
        skill_usage_contract = []

    for skill_name in listed_skills:
        if skill_name not in skill_usage_contract:
            errors.append(
                "Preferred or optional skill "
                f"`{skill_name}` missing from `## Skill Usage Contract`: {INTERNAL_SYNC_CONTROL_CENTER_AGENT}"
            )

    missing_required_skills = sorted(
        INTERNAL_SYNC_CONTROL_CENTER_REQUIRED_SKILLS - set(listed_skills)
    )
    for skill_name in missing_required_skills:
        errors.append(
            f"Required preferred or optional skill `{skill_name}` missing from {INTERNAL_SYNC_CONTROL_CENTER_AGENT}"
        )

    if "Governance files reviewed" not in text:
        errors.append(
            "Missing `Governance files reviewed` output requirement in "
            f"{INTERNAL_SYNC_CONTROL_CENTER_AGENT}"
        )

    if ".github/copilot-instructions.md" not in text or "root `AGENTS.md`" not in text:
        errors.append(
            "Missing explicit governance-review language for `.github/copilot-instructions.md` "
            f"and root `AGENTS.md` in {INTERNAL_SYNC_CONTROL_CENTER_AGENT}"
        )


def validate_legacy_skill_references(errors: list[str]) -> None:
    files_to_check = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".github" / "copilot-instructions.md",
    ]
    files_to_check.extend(sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")))

    for path in files_to_check:
        if not path.exists():
            continue
        if LEGACY_SKILL_IDENTIFIER in read_text(path):
            errors.append(f"Legacy skill reference `{LEGACY_SKILL_IDENTIFIER}` found in {path}")


def validate_internal_skill_reference_files(errors: list[str]) -> None:
    if not (REPO_ROOT / ".github" / "skills" / "internal-code-review" / "SKILL.md").exists():
        return

    for reference_path in INTERNAL_CODE_REVIEW_REFERENCE_PATHS:
        if not (REPO_ROOT / reference_path).exists():
            errors.append(
                "Missing internal code review reference file: "
                f"{reference_path}"
            )


def validate_operation_completion_report_contract(errors: list[str]) -> None:
    copilot_instructions_path = REPO_ROOT / ".github" / "copilot-instructions.md"
    if copilot_instructions_path.exists():
        text = read_text(copilot_instructions_path)
        if OPERATION_COMPLETION_REPORT_SECTION not in text:
            errors.append(
                f"Missing `{OPERATION_COMPLETION_REPORT_SECTION}` in {copilot_instructions_path}"
            )
        for heading in COMPLETION_REPORT_CATEGORY_HEADINGS:
            if heading not in text:
                errors.append(
                    f"Missing completion report category `{heading}` in {copilot_instructions_path}"
                )
        if COMPLETION_REPORT_UNUSED_REASON not in text:
            errors.append(
                "Missing unused-category explanation requirement in "
                f"{copilot_instructions_path}"
            )

    agents_path = REPO_ROOT / "AGENTS.md"
    if agents_path.exists() and AGENTS_COMPLETION_REPORT_POINTER not in read_text(agents_path):
        errors.append(f"Missing completion-report bridge pointer in {agents_path}")

    readme_path = REPO_ROOT / ".github" / "README.md"
    if readme_path.exists():
        text = read_text(readme_path)
        if COMPLETION_REPORT_CONTRACT_SECTION not in text:
            errors.append(f"Missing `{COMPLETION_REPORT_CONTRACT_SECTION}` in {readme_path}")
        for heading in COMPLETION_REPORT_CATEGORY_HEADINGS:
            if heading not in text:
                errors.append(f"Missing completion report category `{heading}` in {readme_path}")
        if COMPLETION_REPORT_UNUSED_REASON not in text:
            errors.append(
                "Missing unused-category explanation requirement in "
                f"{readme_path}"
            )


def validate_sync_agent_completion_report_contract(errors: list[str]) -> None:
    for relative_path in SYNC_AGENT_COMPLETION_REPORT_PATHS:
        agent_path = REPO_ROOT / relative_path
        if not agent_path.exists():
            continue

        text = read_text(agent_path)
        if "## Output Expectations" not in text:
            errors.append(f"Missing `## Output Expectations` in {relative_path}")

        for heading in COMPLETION_REPORT_CATEGORY_HEADINGS:
            if heading not in text:
                errors.append(
                    f"Missing completion report category `{heading}` in {relative_path}"
                )

        if COMPLETION_REPORT_UNUSED_REASON not in text:
            errors.append(
                "Missing unused-category explanation requirement in "
                f"{relative_path}"
            )


def build_report(scope: str, mode: str) -> ValidationReport:
    normalize_scope(scope)
    normalize_mode(mode)

    errors: list[str] = []
    warnings: list[str] = []
    validate_required_paths(errors)
    validate_named_resources(errors)
    validate_inventory(errors)
    validate_repo_profile_references(errors)
    validate_obra_source_of_truth(errors)
    validate_governance_obra_skill_references(errors)
    validate_internal_sync_control_center_contract(errors)
    validate_legacy_skill_references(errors)
    validate_internal_skill_reference_files(errors)
    validate_operation_completion_report_contract(errors)
    validate_sync_agent_completion_report_contract(errors)
    warnings.extend(build_instruction_load_warnings())
    return ValidationReport(errors=errors, warnings=warnings)


def emit_report(report: ValidationReport, fmt: str, report_file: str | None) -> None:
    if fmt == "json":
        payload = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
        if report_file:
            Path(report_file).write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return

    if report.valid:
        if report.warnings:
            warning_output = "\n".join(f"WARNING: {warning}" for warning in report.warnings) + "\n"
            sys.stdout.write(warning_output)
            if report_file:
                Path(report_file).write_text(warning_output, encoding="utf-8")
        print("Validation passed.")
        if report_file:
            with Path(report_file).open("a", encoding="utf-8") as handle:
                handle.write("Validation passed.\n")
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
