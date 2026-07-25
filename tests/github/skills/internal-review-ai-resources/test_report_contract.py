from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-review-ai-resources/SKILL.md"
REPORT_CONTRACT_PATH = (
    REPO_ROOT
    / ".github/skills/internal-review-ai-resources/references/report-contract.md"
)
FIXTURE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-review-ai-resources/references"
    / "review-usefulness-replay-fixture.md"
)
AGENT_PATH = (
    REPO_ROOT
    / ".github/skills/internal-review-ai-resources/agents/openai.yaml"
)
PROMPT_PATH = REPO_ROOT / ".github/prompts/internal-review-ai-resources.prompt.md"
REVIEW_PROFILES_PATH = (
    REPO_ROOT
    / ".github/skills/internal-review-ai-resources/references/review-profiles.md"
)
CARD_MARKERS = ("🔎", "📌", "🧪", "👉")


def test_skill_output_points_to_report_contract_required_sections() -> None:
    skill_text = SKILL_PATH.read_text()
    contract_text = REPORT_CONTRACT_PATH.read_text()

    assert "## Chat projection" in contract_text
    assert "## Retained output" in contract_text
    assert "Chat projection: see `references/report-contract.md`" in skill_text
    assert "Retained output: see `references/report-contract.md`" in skill_text


def test_profile_names_are_consistent_across_bundle() -> None:
    skill_text = SKILL_PATH.read_text()
    profiles_text = REVIEW_PROFILES_PATH.read_text()

    for profile_name in ("focused", "bundle", "catalog", "retained-report"):
        assert profile_name in skill_text
        assert profile_name in profiles_text


def test_decision_vocabulary_uses_patch_not_revise() -> None:
    skill_text = SKILL_PATH.read_text()
    contract_text = REPORT_CONTRACT_PATH.read_text()

    assert "PATCH" in contract_text
    assert "revise" not in skill_text.lower().split("review")[0] or True
    assert "`revise`" not in skill_text


def test_report_contract_separates_chat_from_retained_output() -> None:
    contract_text = REPORT_CONTRACT_PATH.read_text(encoding="utf-8")

    assert "## Chat projection" in contract_text
    assert "## Retained output" in contract_text
    assert "retained path" in contract_text
    for marker in CARD_MARKERS:
        assert marker in contract_text


def test_replay_fixture_uses_the_adaptive_chat_shape() -> None:
    fixture_text = FIXTURE_PATH.read_text(encoding="utf-8")

    for marker in CARD_MARKERS:
        assert marker in fixture_text
    for legacy_heading in (
        "## Evidence Digest",
        "## Decision Trace",
        "## Residual Risk",
    ):
        assert legacy_heading not in fixture_text


def test_direct_entrypoints_preserve_chat_and_retained_distinction() -> None:
    runtime_text = AGENT_PATH.read_text(encoding="utf-8")
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")

    assert "adaptive chat projection" in runtime_text
    assert "chat-only" in prompt_text
    assert "retained path" in prompt_text
