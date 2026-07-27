from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-review-high-level"
SKILL = BUNDLE / "SKILL.md"
RUNTIME = BUNDLE / "agents/openai.yaml"
ANALYSIS = BUNDLE / "references/analysis-dimensions.md"
LENSES = BUNDLE / "references/review-lenses.md"
REMOVED_REFERENCES = (
    BUNDLE / "references" / ("plan-" + "completion-audit.md"),
    BUNDLE / "references" / ("scope-" + "drift.md"),
)
CODE_ORIENTED_CONSUMERS = (
    REPO_ROOT / ".github/skills/internal-debugging/SKILL.md",
    REPO_ROOT / ".github/skills/internal-ddd/SKILL.md",
)


def _bundle_runtime_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8") for path in (SKILL, ANALYSIS, LENSES, RUNTIME)
    )


def test_reviewer_is_independent_non_code_and_report_only() -> None:
    text = SKILL.read_text(encoding="utf-8").lower()
    for marker in (
        "independent",
        "non-code",
        "evidence-first",
        "report-only",
        "no remediation",
    ):
        assert marker in text


def test_bundle_has_no_cross_skill_routing() -> None:
    text = _bundle_runtime_text().lower()
    for marker in (
        "## referenced skills",
        "load /",
        "invoke /",
        "delegate to /",
        "route to /",
    ):
        assert marker not in text


def test_one_adaptive_method_handles_available_baselines() -> None:
    text = SKILL.read_text(encoding="utf-8").lower()
    assert "## review method" in text
    assert "available baseline" in text
    assert "standalone" in text
    assert "change" in text
    assert "plan-to-change" in text
    assert "only when" in text
    assert "## entry modes" not in text


def test_material_findings_are_traceable_and_report_only() -> None:
    text = SKILL.read_text(encoding="utf-8")
    for field in (
        "Evidence",
        "Impact",
        "Severity",
        "Confidence",
        "Recommendation",
        "Fix owner",
        "Expected verification",
    ):
        assert field in text
    lower = text.lower()
    assert "no material findings" in lower
    assert "insufficient evidence" in lower
    assert "omit" in lower


def test_runtime_prompt_projects_the_same_boundary() -> None:
    text = RUNTIME.read_text(encoding="utf-8").lower()
    for marker in (
        "/internal-review-high-level",
        "non-code",
        "evidence-first",
        "report-only",
        "material findings",
        "evidence gaps",
    ):
        assert marker in text


def test_analysis_dimensions_cover_every_approved_artifact_class() -> None:
    text = ANALYSIS.read_text(encoding="utf-8").lower()
    for heading in (
        "## common assurance dimensions",
        "## ai resources",
        "## architectures",
        "## proposals and mature ideas",
        "## documents, policies, plans, and specifications",
    ):
        assert heading in text
    for marker in (
        "scope drift",
        "governance drift",
        "trust boundary",
        "stop condition",
        "decision readiness",
        "lifecycle",
    ):
        assert marker in text


def test_review_lenses_separate_evidence_severity_confidence_and_verdict() -> None:
    text = LENSES.read_text(encoding="utf-8")
    for heading in (
        "## Evidence status",
        "## Severity",
        "## Confidence",
        "## Verdict",
        "## Material finding",
    ):
        assert heading in text
    lower = text.lower()
    assert "observation" in lower
    assert "inference" in lower
    assert "evidence gap" in lower
    assert "no material findings" in lower
    assert "insufficient evidence" in lower


def test_high_level_review_has_a_non_code_boundary() -> None:
    text = SKILL.read_text(encoding="utf-8").lower()
    assert "non-code" in text
    for marker in ("system fit", "cross-cutting", "evidence", "validation"):
        assert marker in text
    for anti_scope in ("code-level", "syntax", "format", "executable behavior"):
        assert anti_scope in text


def test_high_level_review_uses_one_adaptive_method() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "## Review method" in text
    assert "## Entry modes" not in text
    assert "exactly one branch" not in text
    assert "Start with exactly" not in text
    assert "NEEDS INVESTIGATION" not in text


def test_bundle_is_agent_independent_and_pruned() -> None:
    text = _bundle_runtime_text().lower()
    for marker in (
        "agent-mediated",
        "custom agent",
        "persona agent",
        "delegat",
        "custom review agent",
    ):
        assert marker not in text
    assert ANALYSIS.exists()
    assert LENSES.exists()
    assert all(not path.exists() for path in REMOVED_REFERENCES)


def test_public_projection_keeps_simple_emoji_anchors() -> None:
    text = SKILL.read_text(encoding="utf-8")
    section = text.split("## Public projection", 1)[1].split("\n## ", 1)[0]
    for marker in ("🔎", "📌", "🧪", "👉"):
        assert marker in section
    assert "omit" in section.lower()
    assert "exactly four" not in section.lower()


def test_runtime_prompt_matches_the_non_code_boundary() -> None:
    text = RUNTIME.read_text(encoding="utf-8")
    lower = text.lower()
    assert "/internal-review-high-level" in text
    assert "non-code" in lower
    assert "evidence" in lower
    for marker in ("agent-mediated", "custom agent", "delegat", "NEEDS INVESTIGATION"):
        assert marker.lower() not in lower


def test_code_oriented_consumers_do_not_route_to_high_level_review() -> None:
    for path in CODE_ORIENTED_CONSUMERS:
        assert "internal-review-high-level" not in path.read_text(encoding="utf-8")
