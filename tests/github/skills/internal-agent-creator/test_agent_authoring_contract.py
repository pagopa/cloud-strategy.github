from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = ROOT / ".github" / "skills" / "internal-agent-creator"


def read_bundle_file(relative_path: str) -> str:
    return (SKILL_DIR / relative_path).read_text(encoding="utf-8")


def test_skill_routes_to_requirements_and_persona_reference() -> None:
    skill = read_bundle_file("SKILL.md")

    assert "references/requirements-and-persona.md" in skill
    assert "requirements gate" in skill.lower()
    assert "context handoff" in skill.lower()


def test_requirements_and_persona_contract_is_safe_and_behavioral() -> None:
    contract = read_bundle_file("references/requirements-and-persona.md")

    assert "## Requirements Gate" in contract
    assert "## Persona Translation" in contract
    assert "## Name and Path Safety" in contract
    assert "## Context Handoff" in contract
    assert "observable behavior" in contract
    assert "Do not invent credentials" in contract
    assert r"^internal-[a-z0-9]+(?:-[a-z0-9]+)*$" in contract
    assert ".github/agents/" in contract


def test_templates_and_review_checklist_enforce_operating_stance() -> None:
    template = read_bundle_file("references/agent-template.md")
    checklist = read_bundle_file("references/review-checklist.md")

    assert "operating stance" in template.lower()
    assert "prestige biography" in template.lower()
    assert "requirements gate" in checklist.lower()
    assert "context handoff" in checklist.lower()
