import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
VALIDATOR = (
    REPO_ROOT
    / ".github/skills/internal-gateway-critical-master/scripts/validate_critical_output.py"
)
FIXTURES = REPO_ROOT / ".github/skills/internal-gateway-critical-master/fixtures"
VALIDATOR_SPEC = spec_from_file_location("validate_critical_output", VALIDATOR)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
VALIDATOR_MODULE = module_from_spec(VALIDATOR_SPEC)
sys.path.insert(0, str(VALIDATOR.parent))
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_minimal_card_passes_strict() -> None:
    result = run_validator(
        "--file", str(FIXTURES / "critical_output_valid.md"), "--strict"
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_valid_complex_card_passes_strict() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_valid_premortem.md"),
        "--strict",
    )
    assert result.returncode == 0


def test_legacy_section_report_is_rejected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "## Summary\n\nOld summary.\n\n"
        "## Findings\n\nOld findings.\n\n"
        "## Synthesis\n\nOld synthesis.\n\n"
        "## Outcome\n\n`accept-with-risk`\n"
    )
    assert "legacy-section-format" in {finding.code for finding in findings}


def test_missing_plan_marker_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "⚠️ **Critique:** Something is wrong.\n✅ **Advice:** Do this instead.\n"
    )
    assert "missing-plan" in {finding.code for finding in findings}


def test_missing_critique_marker_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** Do something.\n✅ **Advice:** Do this instead.\n"
    )
    assert "missing-critique" in {finding.code for finding in findings}


def test_missing_advice_marker_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** Do something.\n⚠️ **Critique:** Something is wrong.\n"
    )
    assert "missing-advice" in {finding.code for finding in findings}


def test_duplicate_marker_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** First plan.\n"
        "🎯 **Plan:** Duplicate plan.\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "✅ **Advice:** Do this instead.\n"
    )
    assert "duplicate-marker" in {finding.code for finding in findings}


def test_incorrect_marker_order_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "⚠️ **Critique:** Critique before plan.\n"
        "🎯 **Plan:** Plan after critique.\n"
        "✅ **Advice:** Do this instead.\n"
    )
    assert "card-line-order" in {finding.code for finding in findings}


def test_risk_after_advice_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** Do something.\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "✅ **Advice:** Do this instead.\n"
        "💥 **Risk:** Material risk.\n"
    )
    assert "card-line-order" in {finding.code for finding in findings}


def test_question_before_advice_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** Do something.\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "❓ **Question:** What if?\n"
        "✅ **Advice:** Do this instead.\n"
    )
    assert "card-line-order" in {finding.code for finding in findings}


def test_more_than_five_lines_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** Do something.\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "💥 **Risk:** Material risk.\n"
        "💥 **Risk:** Another risk.\n"
        "✅ **Advice:** Do this instead.\n"
        "❓ **Question:** What if?\n"
    )
    assert any(
        finding.code in ("card-line-count", "duplicate-marker") for finding in findings
    )


def test_unexpected_content_line_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** Do something.\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "✅ **Advice:** Do this instead.\n"
        "Some random prose line.\n"
    )
    assert "unexpected-content-line" in {finding.code for finding in findings}


def test_empty_content_after_label_detected() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:**\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "✅ **Advice:** Do this instead.\n"
    )
    assert "unexpected-content-line" in {finding.code for finding in findings}


def test_per_line_word_budget_enforced() -> None:
    long_line = "word " * 35
    findings = VALIDATOR_MODULE.validate_output(
        f"🎯 **Plan:** {long_line.strip()}\n"
        "⚠️ **Critique:** Short critique.\n"
        "✅ **Advice:** Short advice.\n"
    )
    assert "card-line-word-limit" in {finding.code for finding in findings}


def test_total_word_budget_enforced() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Plan:** " + "word " * 35 + "\n"
        "⚠️ **Critique:** " + "word " * 35 + "\n"
        "✅ **Advice:** " + "word " * 35 + "\n"
    )
    assert "total-word-limit" in {finding.code for finding in findings}


def test_localized_labels_accepted_when_emoji_order_valid() -> None:
    findings = VALIDATOR_MODULE.validate_output(
        "🎯 **Piano:** Spostare la validazione.\n"
        "⚠️ **Critica:** La prova centrale scompare.\n"
        "✅ **Consiglio:** Mantenere la CI.\n"
    )
    blocking_codes = {f.code for f in findings if f.severity == "blocking"}
    assert not blocking_codes


def test_cli_format_text_renders_findings() -> None:
    text = (
        "🎯 **Plan:** Do something.\n"
        "⚠️ **Critique:** Something is wrong.\n"
        "Some stray line.\n"
    )
    result = run_validator("--format", "text")
    pass


def test_cli_format_json_returns_finding_list() -> None:
    import json as json_mod

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--format", "json"],
        input=(
            "🎯 **Plan:** Do something.\n"
            "⚠️ **Critique:** Something is wrong.\n"
            "✅ **Advice:** Do this.\n"
            "Extra line.\n"
        ),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    data = json_mod.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "code" in data[0]


def test_cli_format_compact_returns_status_and_counts() -> None:
    import json as json_mod

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--format", "compact"],
        input=(
            "🎯 **Plan:** Do something.\n"
            "⚠️ **Critique:** Something is wrong.\n"
            "✅ **Advice:** Do this.\n"
        ),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    data = json_mod.loads(result.stdout)
    assert "status" in data
    assert "finding_counts" in data


def test_cli_unreadable_file_exits_nonzero_with_stderr() -> None:
    result = run_validator(
        "--file",
        "/nonexistent/path/missing_file.md",
    )
    assert result.returncode != 0
    assert result.stderr.strip() != ""


def test_cli_make_target_includes_strict() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "--strict" in makefile
    assert "critical-validate" in makefile
