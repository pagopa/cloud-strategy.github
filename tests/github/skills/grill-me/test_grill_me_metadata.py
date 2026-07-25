from pathlib import Path

import yaml

SKILL_ROOT = Path(__file__).parents[4] / ".github" / "skills" / "grill-me"


def test_grill_me_metadata_identifies_the_interview_skill() -> None:
    interface = yaml.safe_load(
        (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )["interface"]

    assert interface["display_name"] == "Grill Me"
    assert (
        interface["short_description"]
        == "Relentless interview to sharpen a plan or design"
    )
