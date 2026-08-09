from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = REPO_ROOT / ".github/skills/internal-gateway-idea/scripts/idea_state.py"
FIXTURES = Path(__file__).parent / "fixtures"


def _load_module():
    spec = importlib.util.spec_from_file_location("idea_state_v2", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _state(module, *, state: str = "WAIT_G0", assurance: str = "standard", revision: int = 1, digest: str = "a" * 64, sources: tuple[str, ...] = ()):
    reviewed = revision if state in {"WAIT_G4", "WAIT_G5", "APPROVED"} else None
    approved = revision if state == "APPROVED" else None
    return module.StateV2(
        schema="internal-gateway-idea-state/v2",
        slug="sample",
        revision=revision,
        state=state,
        design_sha256=digest,
        assurance=assurance,
        review_sources=sources,
        reviewed_revision=reviewed,
        approved_revision=approved,
    )


def _g0_payload() -> dict[str, object]:
    return {
        "intent": "Make the idea gateway fail closed.",
        "accepted_decisions": ["Use one mandatory current-gate workflow."],
        "open_decisions": [],
        "constraints": ["No Git mutation."],
        "success_criteria": ["Every gate has executable evidence."],
        "anti_scope": ["Do not change unrelated gateways."],
        "evidence": ["focused tests"],
    }


def test_v2_state_round_trip_is_strict_and_minimal() -> None:
    module = _load_module()
    state = _state(module)

    encoded = module.serialize_state(state)
    parsed = module.parse_state(encoded, expected_slug="sample")

    assert parsed == state
    assert set(json.loads(encoded)) == {
        "schema",
        "slug",
        "revision",
        "state",
        "design_sha256",
        "assurance",
        "review_sources",
        "reviewed_revision",
        "approved_revision",
    }


@pytest.mark.parametrize(
    "value",
    (
        {"schema": "internal-gateway-idea/v1", "slug": "sample"},
        {
            "schema": "internal-gateway-idea-state/v2",
            "slug": "sample",
            "revision": 1,
            "state": "WAIT_G0",
            "design_sha256": "a" * 64,
            "assurance": "standard",
            "review_sources": ["standard", "standard"],
            "reviewed_revision": None,
            "approved_revision": None,
        },
    ),
)
def test_v1_or_duplicate_review_state_fails_closed(value: dict[str, object]) -> None:
    module = _load_module()
    with pytest.raises(module.DesignValidationError):
        module.validate_state(value, expected_slug="sample")


@pytest.mark.parametrize("message, expected", (("OK!", "ok"), ("continua.", "continua"), ("procedi?", "procedi"), (" VA BENE ", "va bene")))
def test_short_approval_normalizes_only_terminal_punctuation(message: str, expected: str) -> None:
    module = _load_module()
    assert module.normalize_short_approval(message) == expected


@pytest.mark.parametrize(
    "message",
    (
        "okay",
        "not ok",
        "ok, implementa",
        "approvo e scrivi il piano",
        "procedi domani",
        "please continua",
        "scrivi il piano",
    ),
)
def test_compound_future_or_execution_intent_cannot_advance(message: str) -> None:
    module = _load_module()
    assert module.normalize_short_approval(message) is None


def test_presented_default_produces_typed_current_gate_event() -> None:
    module = _load_module()
    state = _state(module)
    presented = module.PresentedDecision("resolve-g0", _g0_payload(), "WAIT_G0")

    event = module.adapt_presented_approval(
        "OK!", current_state=state, presented=presented
    )
    result = module.transition_gate(state, event, gate="WAIT_G0")

    assert event.name == "resolve-g0"
    assert result.accepted is True
    assert result.state.state == "WAIT_G1"
    assert result.state.revision == state.revision


def test_future_event_is_rejected_without_state_change() -> None:
    module = _load_module()
    state = _state(module, state="WAIT_G1")
    with pytest.raises(module.DesignValidationError):
        module.validate_event(
            {"event": "resolve-review", "payload": {"disposition": "closed"}},
            current_state=state,
        )

    result = module.transition_gate(
        state, module.TypedEvent("approve", {}), gate="WAIT_G1"
    )
    assert result.state.state == "WAIT_G2"
    assert result.state.revision == state.revision


def test_normal_initialization_creates_only_bounded_two_artifact_pair(tmp_path: Path) -> None:
    module = _load_module()
    assert list(tmp_path.iterdir()) == []

    snapshot = module.initialize_after_g0(
        tmp_path,
        slug="sample",
        decision_payload=_g0_payload(),
        assurance="standard",
    )

    assert snapshot.state.state == "WAIT_G1"
    assert snapshot.state.revision == 1
    assert module.validate_design_text(snapshot.design_text or "", pre_g3=True) <= 300
    assert {path.name for path in tmp_path.iterdir()} == {"design.md", "state.json"}


def test_advance_rejects_an_uninitialized_directory(tmp_path: Path) -> None:
    module = _load_module()
    result = module.main(
        [
            "advance",
            "--root",
            str(tmp_path),
            "--slug",
            "sample",
            "--event",
            "approve",
            "--message",
            "ok",
        ]
    )
    assert result != 0
    assert list(tmp_path.iterdir()) == []


def test_advance_accepts_a_readable_critical_report_at_g3(tmp_path: Path, capsys) -> None:
    module = _load_module()
    design = module.render_bounded_design(_g0_payload())
    (tmp_path / "design.md").write_text(design, encoding="utf-8")
    state = _state(
        module,
        state="WAIT_G3",
        digest=hashlib.sha256(design.encode("utf-8")).hexdigest(),
    )
    (tmp_path / "state.json").write_text(module.serialize_state(state), encoding="utf-8")
    report = """# Critical Analysis

## Scope
Review the typed event boundary.

## Assessment
The boundary is sound.

### Evidence 1 — Explicit state transition
**Critique:** The transition must remain typed.
**Evidence:** The gateway validates event names and payloads.
**Suggestion:** Keep the typed event boundary.
**Why:** It prevents free-form input from advancing state.
**Impact:** An untyped transition could bypass governance.
**Blocking:** false

## Conclusion
**Outcome:** accepted
**Summary:** The current boundary can proceed.
"""

    result = module.main(
        [
            "advance",
            "--root",
            str(tmp_path),
            "--slug",
            "sample",
            "--event",
            "record-readable-review",
            "--payload-json",
            json.dumps({"source": "standard", "report": report}),
            "--compact",
        ]
    )

    assert result == 0
    assert "state=WAIT_G4|" in capsys.readouterr().out


def test_advisory_before_g0_returns_to_wait_g0_without_mandatory_review(tmp_path: Path) -> None:
    module = _load_module()
    started = module.start_advisory_before_g0(
        tmp_path,
        slug="sample",
        bounded_design="## Intent\n\nA bounded advisory design.\n",
        assurance="standard",
    )
    assert started.state.state == "ADVISORY_REVIEW"
    assert started.state.advisory_return_state == "WAIT_G0"

    resumed = module.finish_advisory(started.state)
    assert resumed.state == "WAIT_G0"
    assert resumed.review_sources == ()
    assert resumed.reviewed_revision is None


def test_design_hash_mismatch_reopens_earliest_safe_gate(tmp_path: Path) -> None:
    module = _load_module()
    design = module.render_bounded_design(_g0_payload())
    (tmp_path / "design.md").write_text(design, encoding="utf-8")
    state = _state(module, state="WAIT_G3", digest="0" * 64)
    (tmp_path / "state.json").write_text(module.serialize_state(state), encoding="utf-8")

    recovered = module.load_runtime(tmp_path, slug="sample")
    assert recovered.state.state == "WAIT_G0"
    assert recovered.state.reviewed_revision is None
    assert recovered.state.approved_revision is None


def test_pre_g3_design_cap_is_executable() -> None:
    module = _load_module()
    payload = _g0_payload()
    payload["intent"] = "word " * 305
    with pytest.raises(module.DesignValidationError):
        module.render_bounded_design(payload)


def test_design_fixtures_use_the_v2_markdown_boundary() -> None:
    module = _load_module()
    valid = (FIXTURES / "design-valid.md").read_text(encoding="utf-8")
    invalid = (FIXTURES / "design-invalid.md").read_text(encoding="utf-8")
    assert module.validate_design_text(valid, pre_g3=True) <= 300
    with pytest.raises(module.DesignValidationError):
        module.validate_design_text(invalid, pre_g3=True)


def test_template_skill_and_metadata_share_structured_v2_contract() -> None:
    template = (
        REPO_ROOT / ".github/skills/internal-gateway-idea/references/design-template.md"
    ).read_text(encoding="utf-8")
    skill = (REPO_ROOT / ".github/skills/internal-gateway-idea/SKILL.md").read_text(
        encoding="utf-8"
    )
    metadata = (
        REPO_ROOT / ".github/skills/internal-gateway-idea/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    json_block = template.split("```json", 1)[1].split("```", 1)[0]
    documented_state = json.loads(json_block)
    assert documented_state["schema"] == "internal-gateway-idea-state/v2"
    assert set(documented_state) == {
        "schema",
        "slug",
        "revision",
        "state",
        "design_sha256",
        "assurance",
        "review_sources",
        "reviewed_revision",
        "approved_revision",
    }
    for document in (template, skill, metadata):
        assert "internal-gateway-idea-state/v2" in document
        assert "state.json" in document
        assert "design.md" in document


def test_design_is_replaced_before_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    events: list[str] = []
    original = module.os.replace

    def observe(source: object, target: object) -> None:
        events.append(Path(target).name)
        original(source, target)

    monkeypatch.setattr(module.os, "replace", observe)
    state = _state(module, state="WAIT_G1")
    module.replace_design_then_state(
        tmp_path,
        module.render_bounded_design(_g0_payload()),
        state,
    )

    assert events[:2] == ["design.md", "state.json"]


def test_compact_cli_show_emits_one_line(tmp_path: Path) -> None:
    module = _load_module()
    module.initialize_after_g0(
        tmp_path,
        slug="sample",
        decision_payload=_g0_payload(),
        assurance="standard",
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "inspect",
            "--root",
            str(tmp_path),
            "--slug",
            "sample",
            "--compact",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert completed.stdout.count("\n") == 1
    assert completed.stderr == ""
    assert "WAIT_G1" in completed.stdout
