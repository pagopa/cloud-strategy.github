from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-idea/scripts/critical_report_adapter.py"
)
IDEA_STATE_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-idea/scripts/idea_state.py"
)
TARGET = "tmp/idea/sample/design.md"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "critical_report_adapter", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_idea_state():
    spec = importlib.util.spec_from_file_location(
        "idea_state_v3_adapter_test", IDEA_STATE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


REPORT = """# Critical Analysis

## Scope

Review a proposal to move validation into local developer workflows.

## Assessment

The goal is useful, but the current evidence is incomplete.

### Evidence 1 — Central proof is missing

**Critique:** Local checks do not create a shared record.
**Evidence:** The proposal names local commands but no central result.
**Suggestion:** Keep a central validation step until an equivalent proof exists.
**Why:** A shared control prevents unobserved bypasses.
**Impact:** A missed check can reach delivery without evidence.
**Blocking:** true

### Evidence 2 — The rollout is reversible

**Critique:** The proposed change can be tested on one repository first.
**Evidence:** The rollout description supports a limited pilot.
**Suggestion:** Start with one repository and compare validation results.
**Why:** A bounded pilot reduces the cost of discovering compatibility gaps.
**Impact:** The residual risk is limited to the pilot scope.
**Blocking:** false

## Residual Risks

- Teams may interpret the local check differently.

## Open Questions

- Which system owns the final shared validation record?

## Conclusion

**Outcome:** reopen-analysis
**Summary:** The control boundary must be resolved before rollout.
"""


def test_readable_report_becomes_a_bound_consumer_packet() -> None:
    module = _load_module()

    packet = module.adapt_critical_report(
        REPORT,
        source="standard",
        target_path=TARGET,
        target_revision=3,
    )

    assert set(packet) == {
        "schema",
        "source",
        "target_path",
        "target_revision",
        "outcome",
        "findings",
        "residual_risks",
        "diagnostics",
    }
    assert packet["schema"] == "internal-gateway-critical/full-analysis-v1"
    assert packet["target_path"] == TARGET
    assert packet["target_revision"] == 3
    assert packet["outcome"] == "reopen-analysis"
    assert packet["residual_risks"] == [
        "Teams may interpret the local check differently."
    ]
    assert packet["diagnostics"] == []
    assert packet["findings"] == [
        {
            "id": "C-001",
            "critique": "Local checks do not create a shared record.",
            "recommendation": "Keep a central validation step until an equivalent proof exists.",
            "reason": "A shared control prevents unobserved bypasses.",
            "blocking": True,
            "evidence": ["The proposal names local commands but no central result."],
        },
        {
            "id": "C-002",
            "critique": "The proposed change can be tested on one repository first.",
            "recommendation": "Start with one repository and compare validation results.",
            "reason": "A bounded pilot reduces the cost of discovering compatibility gaps.",
            "blocking": False,
            "evidence": ["The rollout description supports a limited pilot."],
        },
    ]


def test_every_evidence_requires_a_suggestion_and_why() -> None:
    module = _load_module()
    incomplete = REPORT.replace(
        "**Why:** A shared control prevents unobserved bypasses.\n", ""
    )

    with pytest.raises(module.CriticalReportError, match="(?i)why"):
        module.adapt_critical_report(
            incomplete,
            source="standard",
            target_path=TARGET,
            target_revision=3,
        )


def test_no_context_report_is_rejected_before_consumer_ingestion() -> None:
    module = _load_module()
    report = """# Critical Analysis

## Status

Failure: no analysable context was available.
"""

    with pytest.raises(module.CriticalReportError, match="(?i)no analysable context"):
        module.adapt_critical_report(
            report,
            source="standard",
            target_path=TARGET,
            target_revision=3,
        )


def test_every_evidence_requires_explicit_blocking_classification() -> None:
    module = _load_module()
    incomplete = (
        REPORT.replace("**Blocking:** true\n", "")
        .replace("**Blocking:** false\n", "")
        .replace("**Outcome:** reopen-analysis", "**Outcome:** accepted")
    )

    with pytest.raises(module.CriticalReportError, match="(?i)blocking"):
        module.adapt_critical_report(
            incomplete,
            source="standard",
            target_path=TARGET,
            target_revision=3,
        )


def test_non_blocking_findings_can_be_accepted_with_residual_risk() -> None:
    module = _load_module()
    report = REPORT.replace("**Blocking:** true", "**Blocking:** false").replace(
        "**Outcome:** reopen-analysis", "**Outcome:** accepted"
    )

    packet = module.adapt_critical_report(
        report,
        source="standard",
        target_path=TARGET,
        target_revision=3,
    )

    assert packet["outcome"] == "accepted"
    assert all(not finding["blocking"] for finding in packet["findings"])


def test_adapted_report_enters_the_existing_review_boundary() -> None:
    adapter = _load_module()
    idea_state = _load_idea_state()
    state = idea_state.StateV3(
        schema="internal-gateway-idea-state/v3",
        slug="sample",
        revision=3,
        state="WAIT_G3",
        design_sha256="a" * 64,
        assurance="standard",
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        events=(),
    )
    packet = adapter.adapt_critical_report(
        REPORT,
        source="standard",
        target_path=TARGET,
        target_revision=3,
    )

    reviewed = idea_state.record_review(
        state,
        packet,
        g3_approval_event=idea_state.TypedEvent("approve", {}),
        expected_target_path=TARGET,
        expected_revision=3,
    )

    assert reviewed.state == "WAIT_G4"
    assert reviewed.review_sources == ("standard",)
    assert reviewed.reviewed_revision == 3
    assert reviewed.ledger[0].recommendation.startswith("Keep a central")


def test_cli_compact_view_keeps_the_legacy_operator_entrypoint(
    tmp_path, capsys
) -> None:
    module = _load_module()
    report_path = tmp_path / "critical-report.md"
    report_path.write_text(REPORT, encoding="utf-8")

    result = module.main(
        [
            "--file",
            str(report_path),
            "--target-path",
            TARGET,
            "--revision",
            "3",
            "--format",
            "compact",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == (
        '{"status": "ok", "outcome": "reopen-analysis", '
        '"finding_count": 2, "diagnostic_count": 0}'
    )
