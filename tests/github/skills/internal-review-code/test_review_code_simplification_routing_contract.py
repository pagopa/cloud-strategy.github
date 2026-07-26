from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-review-code/SKILL.md"
AGENT_PATH = REPO_ROOT / ".github/skills/internal-review-code/agents/openai.yaml"
CARD_MARKERS = ("🔎", "📌", "🧪", "👉")
CALLER_COUPLING = (
    "agent-mediated",
    "custom agent",
    "delegation is optional",
    "belongs to the custom agent",
)
REVIEW_SPECIFIC_GUIDANCE = (
    "review-anti-patterns.md",
    "identity, cardinality, encoding, error",
    "real-tool/fake-tool parity",
    "references/agentic-eval.md",
)
EXPECTED_SEVERITY_MAPPING = (
    ("Critical", "`B`"),
    ("Required change", "`B`"),
    ("Optional", "`S`"),
    ("Nit", "`S`"),
    ("FYI", ""),
)


FORBIDDEN_RUNTIME_SKILLS = (
    "awesome-copilot-security-review",
    "addyosmani-code-simplification",
    "mattpocock-code-review",
    "superpowers-verification-before-completion",
)


def test_code_review_wrapper_has_no_third_runtime_skill() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    runtime_text = AGENT_PATH.read_text(encoding="utf-8")

    for name in FORBIDDEN_RUNTIME_SKILLS:
        assert name not in skill_text
        assert name not in runtime_text
    assert "specialist security depth" not in skill_text
    assert "route to a separate flow" not in skill_text


def test_runtime_contract_is_independent_of_its_caller() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    prompt_text = AGENT_PATH.read_text(encoding="utf-8")

    for phrase in CALLER_COUPLING:
        assert phrase not in skill_text
        assert phrase not in prompt_text
    assert "## Review preflight" in skill_text
    assert "NEEDS INVESTIGATION" in skill_text
    assert "report-only" in skill_text


def test_adversarial_probes_are_derived_from_target_evidence() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    for phrase in REVIEW_SPECIFIC_GUIDANCE:
        assert phrase not in skill_text
    assert (
        "changed contracts, assumptions, boundaries, and observed evidence"
        in " ".join(skill_text.split())
    )


def test_code_review_wrapper_owns_repository_specific_adversarial_sequence() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    for phrase in (
        "fixed point",
        "target identity",
        "code surface",
        "impacted-validation surface",
        "Standards sources",
        "Spec sources",
        "missing/partial requirements",
        "wrong implementation",
        "scope creep",
        "adversarial probes",
        "green-test anchoring",
        "final coverage counter-analysis",
    ):
        assert phrase in skill_text


def test_code_review_wrapper_owns_only_the_public_chat_projection() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "The core owns review reasoning and severity" in skill_text
    assert "This wrapper owns the public chat projection" in skill_text
    for marker in CARD_MARKERS:
        assert marker in skill_text
    assert "retained review engine" not in skill_text


def test_code_review_runtime_prompt_requests_the_adaptive_projection() -> None:
    prompt_text = AGENT_PATH.read_text(encoding="utf-8")

    assert "adaptive chat projection" in prompt_text
    assert "target and source provenance" in prompt_text
    assert "derive adversarial probes from target evidence" in prompt_text
    assert "NEEDS INVESTIGATION" in prompt_text
    assert "report-only" in prompt_text


def test_skill_owns_a_reachable_fail_closed_gate() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")
    section = text.split("## Review preflight", 1)[1].split("\n## ", 1)[0]

    assert "NEEDS INVESTIGATION" in section
    assert "resolved source cannot be confirmed" in " ".join(section.split())
    assert "report-only" in section


def test_skill_owns_the_engine_accurate_severity_mapping() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")
    section = text.split("## Public projection", 1)[1].split("\n## ", 1)[0]

    for category, target in EXPECTED_SEVERITY_MAPPING:
        assert f"| {category}" in section
        if target:
            assert target in section
    assert "Map the engine's categories to" not in section


def test_code_wrapper_uses_operational_invocation_and_completion_criteria() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    runtime_text = AGENT_PATH.read_text(encoding="utf-8")

    assert "/addyosmani-code-review-and-quality" in skill_text
    assert "## Completion criteria" in skill_text
    assert "/internal-review-code" in runtime_text
    assert "$internal-review-code" not in runtime_text
