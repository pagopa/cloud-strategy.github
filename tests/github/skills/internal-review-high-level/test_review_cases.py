import json
import re
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "review_cases.json"
REQUIRED_CASE_IDS = {
    "standalone-document-contradiction",
    "plan-change-scope-drift",
    "ai-resource-boundary-defect",
    "architecture-trust-boundary-gap",
    "mature-proposal-unsupported-assumption",
    "clean-artifact",
    "evidence-poor-artifact",
    "code-or-remediation-near-miss",
}
ALLOWED_ARTIFACT_CLASSES = {
    "document",
    "change",
    "ai-resource",
    "architecture",
    "proposal",
    "boundary",
}


def test_review_case_fixture_has_required_schema_and_coverage() -> None:
    assert FIXTURE.exists()
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(cases, list)

    by_id = {case["id"]: case for case in cases}
    assert set(by_id) == REQUIRED_CASE_IDS
    assert {case["expected_route"] for case in cases} == {"review", "decline"}

    required_keys = {
        "id",
        "artifact_class",
        "prompt",
        "expected_route",
        "required_signals",
        "forbidden_signals",
    }
    for case in cases:
        assert set(case) == required_keys
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", case["id"])
        assert case["artifact_class"] in ALLOWED_ARTIFACT_CLASSES
        assert case["prompt"].strip()
        assert case["expected_route"] in {"review", "decline"}
        assert all(signal.strip() for signal in case["required_signals"])
        assert all(signal.strip() for signal in case["forbidden_signals"])

        prompt = case["prompt"].lower()
        if case["expected_route"] == "review":
            for forbidden_request in (
                "produce code",
                "write code",
                "return replacement",
                "rewrite the artifact",
            ):
                assert forbidden_request not in prompt
