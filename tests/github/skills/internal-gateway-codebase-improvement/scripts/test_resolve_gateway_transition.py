import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-codebase-improvement/scripts/resolve_gateway_transition.py"
)
SPEC = spec_from_file_location("resolve_gateway_transition", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
resolver = module_from_spec(SPEC)
sys.modules[SPEC.name] = resolver
SPEC.loader.exec_module(resolver)

FIXTURE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-codebase-improvement/fixtures/transition_cases.json"
)
CASES = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_transition_fixture_resolves_expected_state(case: dict[str, object]) -> None:
    state = resolver.ChallengeState(**case["state"])

    decision = resolver.resolve_transition(state)

    assert decision.next_state == case["expected_state"]
    assert (
        decision.approval_invalidated
        == case["expected_approval_invalidated"]
    )
    required_keys = set(case["required_stop_report_keys"])
    assert required_keys <= set(decision.stop_report)
    for key in required_keys:
        assert decision.stop_report[key]


def test_fixture_contains_all_required_transition_cases() -> None:
    assert {case["id"] for case in CASES} == {
        "clear-current-packet",
        "packet-mismatch",
        "stale-approval",
        "open-point-recoverable",
        "recoverable-evidence-exhausted",
        "evidence-unavailable",
        "evidence-unsafe",
        "evidence-out-of-scope",
        "user-declined-evidence",
        "accept-with-risk",
    }
