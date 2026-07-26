import re
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
BASH = SKILLS_ROOT / "internal-bash"
SCRIPT = SKILLS_ROOT / "internal-bash-script"


def _description(bundle: Path) -> str:
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    return str(yaml.safe_load(text.split("---", 2)[1])["description"])


def _runtime(bundle: Path) -> dict[str, str]:
    payload = yaml.safe_load(
        (bundle / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    return payload["interface"]


def _bash_block(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    section = text.split(f"## {heading}", 1)[1]
    return re.search(r"```bash\n(.*?)```", section, re.DOTALL).group(1)


def _run_bash(
    tmp_path: Path, body: str, *args: str
) -> subprocess.CompletedProcess[str]:
    script = tmp_path / "contract.sh"
    script.write_text(body, encoding="utf-8")
    return subprocess.run(
        ["bash", str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_bash_descriptions_separate_lightweight_and_operator_contracts() -> None:
    generic = _description(BASH).lower()
    script = _description(SCRIPT).lower()

    assert "non-operator" in generic
    assert "standalone" in script
    assert "operator-facing" in script


def test_bash_script_routes_lightweight_near_misses_without_preloading() -> None:
    text = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert "embedded shell" in text
    assert "non-operator Bash helper" in text
    assert "internal-bash" in text
    assert "load `internal-bash` first" not in text.lower()


def test_bash_script_uses_repository_test_first_contract() -> None:
    text = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert "Do not add unit tests unless explicitly requested." not in text
    assert "failing focused check before the first implementation edit" in text
    assert "pre-code testability exception" in text


def test_bash_runtime_metadata_names_real_owners() -> None:
    expected = {
        BASH: ("Bash safety and lightweight routing", "$internal-bash"),
        SCRIPT: ("Standalone operator-facing Bash", "$internal-bash-script"),
    }

    for bundle, (short_description, invocation) in expected.items():
        runtime = _runtime(bundle)
        assert runtime["short_description"] == short_description
        assert invocation in runtime["default_prompt"]
        assert "Help with Internal" not in runtime["short_description"]


def test_bash_script_keeps_one_command_check_and_printf_logging() -> None:
    skill = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")
    templates = (SCRIPT / "references/templates.md").read_text(encoding="utf-8")

    assert skill.count("command -v") == 1
    assert "printf 'ℹ️  %s\\n'" in templates
    assert "printf '❌ %s\\n'" in templates
    assert 'echo "ℹ️' not in templates
    assert 'echo "❌' not in templates


def test_minimal_template_rejects_an_option_as_target_value(tmp_path: Path) -> None:
    template = _bash_block(SCRIPT / "references/templates.md", "Minimal Template")

    result = _run_bash(tmp_path, template, "--target", "--help")

    assert result.returncode != 0
    assert "--target requires a value" in result.stderr


def test_argument_parser_defaults_dry_run_and_rejects_option_values(
    tmp_path: Path,
) -> None:
    parser = _bash_block(SCRIPT / "references/templates.md", "Argument Parsing Pattern")
    harness = f"""#!/usr/bin/env bash
set -euo pipefail
log_error() {{ printf '%s\\n' "$*" >&2; }}
usage() {{ :; }}
{parser}
printf 'scope=%s dry_run=%s\\n' "$SCOPE" "$DRY_RUN"
"""

    defaults = _run_bash(tmp_path, harness)
    invalid = _run_bash(tmp_path, harness, "--scope", "--dry-run")

    assert defaults.returncode == 0
    assert defaults.stdout == "scope=repo dry_run=false\n"
    assert invalid.returncode != 0
    assert "--scope requires a value" in invalid.stderr


def test_bash_review_examples_avoid_invalid_or_unsafe_positive_patterns() -> None:
    review = (BASH / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    assert "| SH-M07 | Function body longer than 30 lines" not in review
    assert "| SH-M07 | Function mixes parsing, orchestration, and mutation" in review
    assert 'rm -rf "${name}"' not in review
    assert "process_directory() {" in review
    assert 'cd -- "$base_dir"' in review
    assert 'echo "ℹ️ Processed' not in review


def test_bash_review_rules_match_the_declared_conditional_baseline() -> None:
    review = (BASH / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    assert "Repo mandates Bash" not in review
    assert "Repo convention violation" not in review
    assert "Missing `set -euo pipefail`" not in review
    assert "Bash-specific syntax under a POSIX shell shebang" in review


def test_bash_routing_reserves_standalone_sh_files_for_script_owner() -> None:
    generic = (BASH / "SKILL.md").read_text(encoding="utf-8")

    assert "- `.sh` files and Bash snippets" not in generic
    assert "Sourced `.sh` helpers" in generic
