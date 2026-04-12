from __future__ import annotations

from pathlib import Path

from lib.internal_skills import (
    detect_internal_skill_findings,
    markdown_targets,
    resolve_reference,
    validate_internal_skill,
)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_valid_skill(skill_dir: Path, skill_name: str) -> None:
    write_file(
        skill_dir / "SKILL.md",
        "---\n"
        f"name: {skill_name}\n"
        "description: Keep repository-owned Python skills well shaped.\n"
        "---\n\n"
        f"# {skill_name}\n\n"
        "Use `.github/copilot-sync.manifest.json` only as a generated artifact.\n"
        "Reference `references/guide.md` for examples.\n"
        "```md\n"
        "[Ignored](references/missing.md)\n"
        "```\n",
    )
    write_file(skill_dir / "references/guide.md", "# guide\n")
    write_file(
        skill_dir / "agents/openai.yaml",
        "interface:\n"
        f"  display_name: {skill_name}\n"
        "  short_description: Keep repository-owned Python skills aligned\n"
        f"  default_prompt: Use ${skill_name} for validation.\n",
    )


def test_detect_internal_skill_findings_filters_selected_skills(
    tmp_path: Path,
) -> None:
    root = tmp_path
    (root / ".github").mkdir(parents=True, exist_ok=True)
    write_valid_skill(root / ".github/skills/internal-good", "internal-good")
    (root / ".github/skills/internal-bad").mkdir(parents=True, exist_ok=True)

    selected_findings = detect_internal_skill_findings(
        root, selected_skills={"internal-good"}
    )
    all_findings = detect_internal_skill_findings(root)
    all_codes = {finding.code for finding in all_findings}

    assert selected_findings == []
    assert "missing-skill-md" in all_codes


def test_validate_internal_skill_reports_metadata_and_reference_issues(
    tmp_path: Path,
) -> None:
    root = tmp_path
    (root / ".github").mkdir(parents=True, exist_ok=True)
    skill_dir = root / ".github/skills/internal-demo"
    write_file(
        skill_dir / "SKILL.md",
        "---\n"
        "name: internal-other\n"
        "description: Validate metadata for internal skills carefully.\n"
        "---\n\n"
        "# internal-demo\n\n"
        "[Missing](references/missing.md)\n\n"
        "```md\n"
        "[Ignored](references/ignored.md)\n"
        "```\n",
    )
    write_file(
        skill_dir / "agents/openai.yaml",
        "interface:\n"
        "  display_name: Demo Skill\n"
        "  short_description: Too short\n"
        "  default_prompt: Use the validator.\n",
    )

    findings = validate_internal_skill(root, skill_dir)
    finding_codes = {finding.code for finding in findings}
    missing_reference_findings = [
        finding for finding in findings if finding.code == "missing-local-reference"
    ]

    assert "skill-name-mismatch" in finding_codes
    assert "short-description-length" in finding_codes
    assert "default-prompt-skill-mention" in finding_codes
    assert len(missing_reference_findings) == 1


def test_markdown_targets_and_resolve_reference_support_repo_and_skill_paths(
    tmp_path: Path,
) -> None:
    root = tmp_path
    skill_dir = root / ".github/skills/internal-demo"
    source_file = skill_dir / "SKILL.md"
    write_file(root / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(skill_dir / "references/example.md", "# Example\n")
    text = (
        "[Repo](.github/copilot-instructions.md)\n"
        "[Local](references/example.md)\n"
        "`scripts/run.py`\n"
        "`tmp/generated.md`\n"
    )

    targets = markdown_targets(text)

    assert ".github/copilot-instructions.md" in targets
    assert "references/example.md" in targets
    assert "scripts/run.py" in targets
    assert (
        resolve_reference(
            root, skill_dir, source_file, ".github/copilot-instructions.md"
        )
        == root / ".github/copilot-instructions.md"
    )
    assert resolve_reference(root, skill_dir, source_file, "references/example.md") == (
        skill_dir / "references/example.md"
    )
    assert resolve_reference(root, skill_dir, source_file, "tmp/generated.md") is None
    assert (
        resolve_reference(root, skill_dir, source_file, "https://example.com") is None
    )
