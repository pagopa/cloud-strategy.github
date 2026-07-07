from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".github/skills/internal-gateway-writing-plans/SKILL.md"
AGENT_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-writing-plans/agents/openai.yaml"
)


def test_skill_requires_hhmm_filenames_for_retained_artifacts() -> None:
    text = SKILL_PATH.read_text()

    assert "tmp/superpowers/plans/YYYY-MM-DD-HHMM-<feature-name>.md" in text
    assert "tmp/superpowers/specs/YYYY-MM-DD-HHMM-<topic>-design.md" in text


def test_agent_prompt_mentions_hhmm_filenames_for_plan_and_spec() -> None:
    text = AGENT_PATH.read_text()

    assert "YYYY-MM-DD-HHMM-<feature-name>.md" in text
    assert "YYYY-MM-DD-HHMM-<topic>-design.md" in text
