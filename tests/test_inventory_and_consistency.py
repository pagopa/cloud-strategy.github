from __future__ import annotations

from pathlib import Path

from lib.catalog_checks import check_superpowers_import_naming, run_consistency_checks
from lib.inventory import build_inventory_markdown


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_inventory_markdown_lists_catalog_sections(tmp_path: Path) -> None:
    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(
        tmp_path / ".github/agents/internal-delivery-operator.agent.md",
        "---\nname: internal-delivery-operator\ntools: [read]\n---\n",
    )
    write_file(
        tmp_path / ".github/instructions/internal-python.instructions.md",
        "---\ndescription: Python\napplyTo: '**/*.py'\n---\n",
    )
    write_file(
        tmp_path / ".github/skills/internal-catalog/SKILL.md",
        "---\nname: internal-catalog\ndescription: Catalog helper\n---\n",
    )
    write_file(
        tmp_path / ".github/prompts/internal-agent-plan-next-step.prompt.md",
        "---\ndescription: Planning next step\n---\n",
    )

    inventory = build_inventory_markdown(tmp_path)

    assert "## Instructions" in inventory
    assert "## Prompts" in inventory
    assert "- `.github/instructions/internal-python.instructions.md`" in inventory
    assert "- `.github/skills/internal-catalog/SKILL.md`" in inventory
    assert "- `.github/agents/internal-delivery-operator.agent.md`" in inventory
    assert "- `.github/prompts/internal-agent-plan-next-step.prompt.md`" in inventory


def test_run_consistency_checks_flags_prompt_inventory_drift(tmp_path: Path) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/prompts/internal-agent-review-next-actions.prompt.md",
        "---\ndescription: Review next actions\n---\n",
    )
    write_file(
        tmp_path / ".github/INVENTORY.md",
        "# Copilot Inventory\n\n"
        "## Instructions\n\nNo instruction files currently ship in the live catalog.\n\n"
        "## Skills\n\nNo skill files currently ship in the live catalog.\n\n"
        "## Agents\n\nNo agent files currently ship in the live catalog.\n",
    )
    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/prompts/internal-agent-review-next-actions.prompt.md",
        "inventory-missing-entry",
    ) in findings_by_path


def test_run_consistency_checks_flags_prompt_contract_gaps(tmp_path: Path) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/prompts/internal-invalid.prompt.md",
        "---\n"
        "name: internal-mismatch\n"
        "description: Broken prompt contract\n"
        "---\n\n"
        "No reusable inputs here.\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/prompts/internal-invalid.prompt.md",
        "prompt-name-mismatch",
    ) in findings_by_path
    assert (
        ".github/prompts/internal-invalid.prompt.md",
        "prompt-missing-agent",
    ) in findings_by_path
    assert (
        ".github/prompts/internal-invalid.prompt.md",
        "prompt-missing-input-placeholder",
    ) in findings_by_path


def test_run_consistency_checks_flags_broken_prompt_local_links(tmp_path: Path) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/prompts/internal-valid.prompt.md",
        "---\n"
        "name: internal-valid\n"
        "agent: agent\n"
        "description: Valid prompt metadata\n"
        "---\n\n"
        "Prompt target:\n"
        "${input:subject:Describe the target.}\n\n"
        "See [missing guide](../docs/missing.md).\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/prompts/internal-valid.prompt.md",
        "broken-local-link",
    ) in findings_by_path


def test_run_consistency_checks_flags_inventory_drift_and_missing_tools(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/INVENTORY.md",
        "# Copilot Inventory\n\n## Instructions\n\nNo instruction files currently ship in the live catalog.\n\n## Skills\n\nNo skill files currently ship in the live catalog.\n\n## Agents\n\nNo agent files currently ship in the live catalog.\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\n---\n\n# Internal Sync\n",
    )

    findings = run_consistency_checks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "inventory-missing-entry" in finding_codes
    assert "internal-agent-missing-tools" in finding_codes


def test_run_consistency_checks_flags_empty_and_invalid_tools_contracts(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md`.\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-empty.agent.md",
        "---\nname: internal-empty\ntools: []\n---\n\n# Empty\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-invalid.agent.md",
        "---\nname: internal-invalid\ntools:\n  - read\n  - 1\n---\n\n# Invalid\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/agents/internal-empty.agent.md",
        "internal-agent-missing-tools",
    ) in findings_by_path
    assert (
        ".github/agents/internal-invalid.agent.md",
        "internal-agent-invalid-tools",
    ) in findings_by_path


def test_run_consistency_checks_flags_invalid_imported_asset_override_registry(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md`.\n",
    )
    write_file(
        tmp_path / ".github/skills/obra-demo/SKILL.md",
        "---\nname: obra-demo\ndescription: Imported workflow.\n---\n",
    )
    write_file(
        tmp_path
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml",
        "overrides:\n"
        "  - id: bad-entry\n"
        "    target_path: .github/skills/obra-demo/SKILL.md\n"
        "    lifecycle_mode: support-only\n"
        "    apply_strategy: ad-hoc\n"
        "    approval: pending\n"
        "    patch_path: patches/missing.patch\n"
        "    expected_content_hash: short\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "imported-asset-override-approval-missing" in finding_codes
    assert "imported-asset-override-invalid-lifecycle" in finding_codes
    assert "imported-asset-override-invalid-apply-strategy" in finding_codes
    assert "imported-asset-override-patch-missing" in finding_codes
    assert "imported-asset-override-invalid-hash" in finding_codes


def write_superpowers_normalization_reference(root: Path) -> None:
    write_file(
        root
        / ".github/skills/local-agent-sync-external-resources/references/superpowers-normalization.yaml",
        "version: 1\n"
        "source_family: obra/superpowers\n"
        "local_prefix: superpowers-\n"
        "blocked_local_prefixes:\n"
        "  - obra-\n"
        "blocked_managed_reference_prefix: 'superpowers:'\n"
        "managed_skills:\n"
        "  - upstream: demo\n"
        "    legacy_local: obra-demo\n"
        "    local: superpowers-demo\n"
        "managed_patches:\n"
        "  - legacy_path: patches/obra-demo.patch\n"
        "    path: patches/superpowers-demo.patch\n"
        "live_scan:\n"
        "  include:\n"
        "    - .github/agents\n"
        "    - .github/skills\n"
        "  ignored_files:\n"
        "    - README.md\n"
        "    - CHANGELOG.md\n"
        "    - superpowers-normalization.yaml\n",
    )


def test_check_superpowers_import_naming_flags_legacy_drift(tmp_path: Path) -> None:
    write_superpowers_normalization_reference(tmp_path)
    write_file(
        tmp_path / ".github/skills/obra-demo/SKILL.md",
        "---\nname: obra-demo\ndescription: Demo.\n---\n\nUse superpowers:demo.\n",
    )
    write_file(
        tmp_path / ".github/agents/local-demo.agent.md",
        "---\nname: local-demo\ntools: [read]\n---\n\n- `obra-demo`\n- `superpowers:demo`\n",
    )
    write_file(
        tmp_path
        / ".github/skills/local-agent-sync-external-resources/patches/obra-demo.patch",
        "diff --git a/.github/skills/obra-demo/SKILL.md b/.github/skills/obra-demo/SKILL.md\n",
    )

    findings = check_superpowers_import_naming(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "superpowers-import-legacy-skill-directory" in finding_codes
    assert "superpowers-import-skill-name-mismatch" in finding_codes
    assert "superpowers-import-legacy-reference" in finding_codes
    assert "superpowers-import-upstream-reference" in finding_codes


def test_check_superpowers_import_naming_ignores_reference_legacy_map(
    tmp_path: Path,
) -> None:
    write_superpowers_normalization_reference(tmp_path)
    write_file(
        tmp_path / ".github/skills/superpowers-demo/SKILL.md",
        "---\nname: superpowers-demo\ndescription: Demo.\n---\n",
    )

    findings = check_superpowers_import_naming(tmp_path)

    assert findings == []


def test_run_consistency_checks_flags_legacy_repo_owned_agent_skill_headings(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md`.\n",
    )
    write_file(
        tmp_path / ".github/agents/local-demo.agent.md",
        "---\nname: local-demo\ntools: [read]\n---\n\n"
        "# Local Demo\n\n"
        "## Preferred/Optional Skills\n\n"
        "- `local-demo`\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/agents/local-demo.agent.md",
        "repo-owned-agent-legacy-skill-heading",
    ) in findings_by_path


def test_run_consistency_checks_flags_skill_usage_contract_without_optional_support(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md`.\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-demo.agent.md",
        "---\nname: internal-demo\ntools: [read]\n---\n\n"
        "# Internal Demo\n\n"
        "## Mandatory Engine Skills\n\n"
        "- `internal-demo`\n\n"
        "## Skill Usage Contract\n\n"
        "- `internal-demo`: Use when the skill is mandatory.\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/agents/internal-demo.agent.md",
        "repo-owned-agent-skill-usage-without-optional-support",
    ) in findings_by_path


def test_run_consistency_checks_flags_unallowlisted_instruction_apply_to_overlap(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/instructions/internal-one.instructions.md",
        "---\ndescription: One\napplyTo: '**/*.txt'\n---\n",
    )
    write_file(
        tmp_path / ".github/instructions/internal-two.instructions.md",
        "---\ndescription: Two\napplyTo: '**/*.txt'\n---\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_code = {finding.code for finding in findings}

    assert "instruction-applyto-overlap" in findings_by_code


def test_run_consistency_checks_allows_intentional_shell_apply_to_overlap(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/instructions/awesome-copilot-shell.instructions.md",
        "---\ndescription: Shell\napplyTo: '**/*.sh'\n---\n",
    )
    write_file(
        tmp_path / ".github/instructions/internal-bash.instructions.md",
        "---\ndescription: Bash\napplyTo: '**/*.sh'\n---\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_code = {finding.code for finding in findings}

    assert "instruction-applyto-overlap" not in findings_by_code


def test_run_consistency_checks_allows_intentional_composite_action_apply_to_overlap(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/instructions/internal-github-actions.instructions.md",
        "---\ndescription: GitHub Actions\napplyTo: '**/workflows/**,**/actions/**/action.y*ml'\n---\n",
    )
    write_file(
        tmp_path
        / ".github/instructions/internal-github-action-composite.instructions.md",
        "---\ndescription: Composite actions\napplyTo: '**/actions/**/action.y*ml'\n---\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_code = {finding.code for finding in findings}

    assert "instruction-applyto-overlap" not in findings_by_code
