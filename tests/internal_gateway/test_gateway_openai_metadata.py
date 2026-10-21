from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"
GATEWAYS = (
    "internal-gateway-critical-master",
    "internal-gateway-execute-plans",
    "internal-gateway-idea",
    "internal-gateway-simple-task",
    "internal-gateway-writing-plans",
)
EXPLICIT_ONLY = ("internal-gateway-execute-plans", "internal-gateway-idea")
MAX_DEFAULT_PROMPT_WORDS = 60


def _metadata(name: str) -> dict[str, object]:
    return yaml.safe_load(
        (SKILLS_ROOT / name / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )


def _prompt(name: str) -> str:
    return _metadata(name)["interface"]["default_prompt"]


@pytest.mark.parametrize("name", EXPLICIT_ONLY)
def test_explicit_only_gateways_disable_implicit_invocation(name: str) -> None:
    assert _metadata(name)["policy"] == {"allow_implicit_invocation": False}


@pytest.mark.parametrize("name", GATEWAYS)
def test_default_prompt_is_a_short_codex_pointer(name: str) -> None:
    prompt = _prompt(name)
    words = len(prompt.split())
    assert words <= MAX_DEFAULT_PROMPT_WORDS, f"{name} default_prompt has {words} words"
    assert f"${name}" in prompt


def test_executor_prompt_names_its_implementer_as_a_cross_skill_route() -> None:
    assert "/mattpocock-implement" in _prompt("internal-gateway-execute-plans")


@pytest.mark.parametrize(
    "name", [gateway for gateway in GATEWAYS if gateway != "internal-gateway-execute-plans"]
)
def test_other_gateway_prompts_never_mention_the_executor(name: str) -> None:
    assert "$internal-gateway-execute-plans" not in _prompt(name)


def test_idea_prompt_loads_the_spec_owner_only_on_demand() -> None:
    assert "$mattpocock-to-spec" not in _prompt("internal-gateway-idea")
