from __future__ import annotations

import json
from pathlib import Path


def read_markdownlint_config() -> dict[str, object]:
    raw_text = Path(".markdownlint-cli2.jsonc").read_text(encoding="utf-8")
    json_text = "\n".join(
        line for line in raw_text.splitlines() if not line.lstrip().startswith("//")
    )
    return json.loads(json_text)


def test_markdownlint_ignores_local_venv_and_preserved_upstream_assets() -> None:
    config = read_markdownlint_config()
    ignores = config["ignores"]

    assert "tmp/**" in ignores
    assert ".github/scripts/.venv/**" in ignores
    assert ".github/instructions/awesome-copilot-*.instructions.md" in ignores
    assert ".github/skills/antigravity-*/**" in ignores
    assert ".github/skills/awesome-copilot-*/**" in ignores
    assert ".github/skills/mattpocock-*/**" in ignores
    assert ".github/skills/openai-*/**" in ignores
    assert ".github/skills/superpowers-*/**" in ignores


def test_markdownlint_config_documents_why_special_paths_are_ignored() -> None:
    config_text = Path(".markdownlint-cli2.jsonc").read_text(encoding="utf-8")

    assert "dedicated contract tests cover tmp/superpowers artifacts" in config_text
    assert "generated tooling state" in config_text
    assert "Preserve imported awesome-copilot instructions verbatim" in config_text
    assert "Preserve imported support skill families verbatim" in config_text
