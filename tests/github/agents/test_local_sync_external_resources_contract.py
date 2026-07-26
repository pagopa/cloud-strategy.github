from pathlib import Path

AGENT_PATH = (
    Path(__file__).resolve().parents[3]
    / ".github/agents"
    / ("local-sync-external-resources" + ".agent.md")
)


def test_post_apply_validation_actions_are_bounded() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "focused validation" in text
    assert "its own next action" in text
    assert "remaining declared validations" in text
    assert "one subsequent terminal action" in text
    assert "short-circuit" in text
    assert "Stop on the first failure" in text


def test_sync_contract_preserves_safety_boundaries() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "Bare `sync` means `apply`; never promote" in text
    assert "Run networked `prepare` only when the user explicitly requests" in text
    assert "Treat `--allow-dirty` as explicit risk acceptance" in text
    assert "Stop when the request would change manifest scope" in text
    assert "bare `sync` may run networked `prepare`" not in text
    assert "infer `--allow-dirty`" not in text
    assert "modify the sync manifest during an apply run" not in text
