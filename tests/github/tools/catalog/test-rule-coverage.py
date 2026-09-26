from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Callable

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TOOLS_ROOT = REPO_ROOT / ".github/tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from catalog.rules import (  # noqa: E402
    check_bridge_references,
    check_broken_local_links,
    check_duplicate_frontmatter_names,
    check_external_resource_manifest,
    check_imported_asset_overrides,
    check_internal_agent_contracts,
    check_inventory_matches_filesystem,
    check_prompt_contracts,
    check_repo_owned_agent_sections,
    check_required_bridge_files,
    check_residual_instruction_family_references,
    check_source_instruction_contracts,
    check_superpowers_import_naming,
)
from common.findings import Finding  # noqa: E402

RuleCase = Callable[[Path], list[Finding]]


def _write(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _frontmatter(
    name: str = "internal-example", description: str = "Use when testing fixtures."
) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n## When to use\n\n- Fixture.\n"


def _source_instruction_missing(root: Path) -> list[Finding]:
    _write(
        root, ".github/instructions/example.instructions.md", "---\n---\nShort body.\n"
    )
    return check_source_instruction_contracts(root)


def _source_instruction_overgrown(root: Path) -> list[Finding]:
    body = (
        "optimized for Copilot code review and should produce only evidenced findings\n"
    )
    body += "\n".join("detail" for _ in range(221))
    _write(
        root,
        ".github/instructions/example.instructions.md",
        "---\ndescription: Review fixture\napplyTo: '**/*.py'\nexcludeAgent: cloud-agent\n---\n"
        + body,
    )
    return check_source_instruction_contracts(root)


def _required_bridge_file(root: Path, missing: str) -> list[Finding]:
    files = {
        "AGENTS.md": "# Agents\n",
        ".github/copilot-instructions.md": "This file is only for GitHub.com Copilot code review.\nDo not treat this file as instructions for coding agents, local CLIs, or scripts.\n",
        ".github/instructions/copilot-code-review.instructions.md": "---\ndescription: Review\napplyTo: '**/*'\nexcludeAgent: cloud-agent\n---\n",
        ".github/INVENTORY.md": "# Inventory\n",
    }
    for relative_path, content in files.items():
        if relative_path != missing:
            _write(root, relative_path, content)
    return check_required_bridge_files(root)


def _inventory_missing(root: Path) -> list[Finding]:
    _write(root, ".github/agents/example.agent.md", "---\nname: example\n---\n")
    _write(
        root,
        ".github/INVENTORY.md",
        "# Inventory\n\n## Agents\n\nNo agent files currently ship in the live catalog.\n",
    )
    return check_inventory_matches_filesystem(root)


def _inventory_stale(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/INVENTORY.md",
        "# Inventory\n\n## Agents\n\n- `.github/agents/stale.agent.md`\n",
    )
    return check_inventory_matches_filesystem(root)


def _bridge_reference(root: Path, content: str) -> list[Finding]:
    _write(root, "AGENTS.local.md", content)
    return check_bridge_references(root)


def _copilot_reference(root: Path, content: str) -> list[Finding]:
    _write(root, "AGENTS.local.md", "Local policy; see .github/INVENTORY.md.\n")
    _write(root, ".github/copilot-instructions.md", content)
    return check_bridge_references(root)


def _internal_agent(root: Path, frontmatter: str) -> list[Finding]:
    _write(
        root, ".github/agents/internal-example.agent.md", frontmatter + "\n# Agent\n"
    )
    return check_internal_agent_contracts(root)


def _repo_agent_section(root: Path, section: str) -> list[Finding]:
    _write(root, ".github/agents/internal-example.agent.md", f"# Agent\n\n{section}\n")
    return check_repo_owned_agent_sections(root)


def _duplicate_frontmatter(root: Path) -> list[Finding]:
    _write(root, ".github/agents/internal-one.agent.md", "---\nname: duplicate\n---\n")
    _write(root, ".github/agents/internal-two.agent.md", "---\nname: duplicate\n---\n")
    return check_duplicate_frontmatter_names(root)


def _prompt(
    root: Path, frontmatter: str, body: str = "${input:request}\n"
) -> list[Finding]:
    _write(root, ".github/prompts/example.prompt.md", frontmatter + "\n" + body)
    return check_prompt_contracts(root)


def _residual_reference(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/internal-example/SKILL.md",
        "The retired path is `.github/copilot-code-review-instructions.md`.\n",
    )
    return check_residual_instruction_family_references(root)


def _override_registry(root: Path, entry: dict[str, object]) -> list[Finding]:
    registry = ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    _write(root, registry, yaml.safe_dump({"overrides": [entry]}, sort_keys=False))
    return check_imported_asset_overrides(root)


def _valid_override_entry(root: Path) -> dict[str, object]:
    target = _write(
        root, ".github/skills/anthropic-example/SKILL.md", "---\nname: example\n---\n"
    )
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/fix.patch",
        "patch\n",
    )
    return {
        "id": "override-1",
        "target_path": ".github/skills/anthropic-example/SKILL.md",
        "patch_path": "references/fix.patch",
        "expected_content_hash": hashlib.sha256(target.read_bytes()).hexdigest(),
        "approval": "explicit-user-counter-validated",
        "lifecycle_mode": "post-refresh-patch",
        "apply_strategy": "git-apply",
    }


def _override_invalid_yaml(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml",
        "overrides: [\n",
    )
    return check_imported_asset_overrides(root)


def _override_missing_list(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml",
        "overrides: {}\n",
    )
    return check_imported_asset_overrides(root)


def _override_invalid_entry(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml",
        "overrides:\n  - invalid\n",
    )
    return check_imported_asset_overrides(root)


def _override_missing_id(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry.pop("id")
    return _override_registry(root, entry)


def _override_duplicate_id(root: Path) -> list[Finding]:
    first = _valid_override_entry(root)
    second_target = _write(
        root, ".github/skills/anthropic-second/SKILL.md", "---\nname: second\n---\n"
    )
    second = {
        **first,
        "target_path": ".github/skills/anthropic-second/SKILL.md",
        "expected_content_hash": hashlib.sha256(second_target.read_bytes()).hexdigest(),
    }
    registry = ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    _write(
        root,
        registry,
        yaml.safe_dump(
            {"overrides": [first, second | {"id": first["id"]}]}, sort_keys=False
        ),
    )
    return check_imported_asset_overrides(root)


def _override_missing_target(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry.pop("target_path")
    return _override_registry(root, entry)


def _override_duplicate_target(root: Path) -> list[Finding]:
    first = _valid_override_entry(root)
    second = {**first, "id": "override-2"}
    registry = ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    _write(
        root, registry, yaml.safe_dump({"overrides": [first, second]}, sort_keys=False)
    )
    return check_imported_asset_overrides(root)


def _override_target_not_imported(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["target_path"] = ".github/skills/internal-example/SKILL.md"
    return _override_registry(root, entry)


def _override_target_missing(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    target = root / ".github/skills/anthropic-example/SKILL.md"
    target.unlink()
    return _override_registry(root, entry)


def _override_approval_missing(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["approval"] = "pending"
    return _override_registry(root, entry)


def _override_invalid_lifecycle(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["lifecycle_mode"] = "manual"
    return _override_registry(root, entry)


def _override_invalid_apply_strategy(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["apply_strategy"] = "copy"
    return _override_registry(root, entry)


def _override_missing_patch(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry.pop("patch_path")
    return _override_registry(root, entry)


def _override_patch_missing(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["patch_path"] = "references/missing.patch"
    return _override_registry(root, entry)


def _override_invalid_hash(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["expected_content_hash"] = "bad"
    return _override_registry(root, entry)


def _override_hash_mismatch(root: Path) -> list[Finding]:
    entry = _valid_override_entry(root)
    entry["expected_content_hash"] = "0" * 64
    return _override_registry(root, entry)


def _manifest_missing(root: Path) -> list[Finding]:
    return check_external_resource_manifest(root)


def _manifest_invalid_yaml(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml",
        "version: [\n",
    )
    return check_external_resource_manifest(root)


def _manifest_invalid_shape(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml",
        "version: 2\nsources: {}\n",
    )
    return check_external_resource_manifest(root)


def _manifest_duplicate_target(root: Path) -> list[Finding]:
    payload = {
        "version": 1,
        "sources": {
            "source": {
                "assets": [
                    {"local": ".github/skills/example-one/SKILL.md"},
                    {"local": ".github/skills/example-one/SKILL.md"},
                ]
            }
        },
    }
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml",
        yaml.safe_dump(payload, sort_keys=False),
    )
    return check_external_resource_manifest(root)


def _superpowers_name_mismatch(root: Path) -> list[Finding]:
    local = ".github/skills/superpowers-example"
    _write(root, f"{local}/SKILL.md", "---\nname: wrong-name\n---\n")
    payload = {
        "version": 1,
        "sources": {
            "obra-superpowers": {
                "assets": [{"local": local, "canonical_name": "superpowers-example"}]
            }
        },
    }
    _write(
        root,
        ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml",
        yaml.safe_dump(payload, sort_keys=False),
    )
    return check_superpowers_import_naming(root)


def _broken_local_link(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/skills/internal-example/SKILL.md",
        "[missing](references/nope.md)\n",
    )
    return check_broken_local_links(root)


CATALOG_RULE_CASES: list[tuple[str, RuleCase]] = [
    ("source-instruction-missing-description", _source_instruction_missing),
    ("source-instruction-missing-apply-to", _source_instruction_missing),
    ("source-instruction-missing-exclude-agent", _source_instruction_missing),
    ("source-instruction-missing-review-statement", _source_instruction_missing),
    ("source-instruction-overgrown", _source_instruction_overgrown),
    ("missing-bridge-file", lambda root: _required_bridge_file(root, "AGENTS.md")),
    ("inventory-missing-entry", _inventory_missing),
    ("inventory-stale-entry", _inventory_stale),
    (
        "agents-missing-inventory-reference",
        lambda root: _bridge_reference(root, "# Agents\n"),
    ),
    (
        "copilot-instructions-missing-review-scope",
        lambda root: _copilot_reference(
            root,
            "Do not treat this file as instructions for coding agents, local CLIs, or scripts.\n",
        ),
    ),
    (
        "copilot-instructions-missing-runtime-boundary",
        lambda root: _copilot_reference(
            root,
            "This file is only for GitHub.com Copilot code review.\n",
        ),
    ),
    (
        "internal-agent-missing-tools",
        lambda root: _internal_agent(root, "---\nname: internal-example\n---\n"),
    ),
    (
        "internal-agent-invalid-tools",
        lambda root: _internal_agent(
            root, "---\nname: internal-example\ntools: 1\n---\n"
        ),
    ),
    (
        "internal-agent-legacy-frontmatter",
        lambda root: _internal_agent(
            root, "---\nname: internal-example\ntools: shell\ninfer: true\n---\n"
        ),
    ),
    (
        "internal-agent-legacy-tool-id",
        lambda root: _internal_agent(
            root, "---\nname: internal-example\ntools: terminalCommand\n---\n"
        ),
    ),
    (
        "repo-owned-agent-legacy-skill-heading",
        lambda root: _repo_agent_section(root, "## Preferred/Optional Skills"),
    ),
    (
        "repo-owned-agent-skill-usage-without-optional-support",
        lambda root: _repo_agent_section(root, "## Skill Usage Contract"),
    ),
    ("duplicate-frontmatter-name", _duplicate_frontmatter),
    (
        "prompt-missing-name",
        lambda root: _prompt(
            root, "---\nagent: internal-example\ndescription: Prompt fixture\n---"
        ),
    ),
    (
        "prompt-name-mismatch",
        lambda root: _prompt(
            root,
            "---\nname: other\nagent: internal-example\ndescription: Prompt fixture\n---",
        ),
    ),
    (
        "prompt-missing-agent",
        lambda root: _prompt(
            root, "---\nname: example\ndescription: Prompt fixture\n---"
        ),
    ),
    (
        "prompt-generic-agent",
        lambda root: _prompt(
            root, "---\nname: example\nagent: agent\ndescription: Prompt fixture\n---"
        ),
    ),
    (
        "prompt-missing-description",
        lambda root: _prompt(root, "---\nname: example\nagent: internal-example\n---"),
    ),
    (
        "prompt-missing-input-placeholder",
        lambda root: _prompt(
            root,
            "---\nname: example\nagent: internal-example\ndescription: Prompt fixture\n---",
            "No input.\n",
        ),
    ),
    ("residual-instruction-reference", _residual_reference),
    ("imported-asset-overrides-invalid-yaml", _override_invalid_yaml),
    ("imported-asset-overrides-missing-list", _override_missing_list),
    ("imported-asset-override-invalid-entry", _override_invalid_entry),
    ("imported-asset-override-missing-id", _override_missing_id),
    ("imported-asset-override-duplicate-id", _override_duplicate_id),
    ("imported-asset-override-missing-target", _override_missing_target),
    ("imported-asset-override-duplicate-target", _override_duplicate_target),
    ("imported-asset-override-target-not-imported", _override_target_not_imported),
    ("imported-asset-override-target-missing", _override_target_missing),
    ("imported-asset-override-approval-missing", _override_approval_missing),
    ("imported-asset-override-invalid-lifecycle", _override_invalid_lifecycle),
    (
        "imported-asset-override-invalid-apply-strategy",
        _override_invalid_apply_strategy,
    ),
    ("imported-asset-override-missing-patch", _override_missing_patch),
    ("imported-asset-override-patch-missing", _override_patch_missing),
    ("imported-asset-override-invalid-hash", _override_invalid_hash),
    ("imported-asset-override-hash-mismatch", _override_hash_mismatch),
    ("external-resource-manifest-missing", _manifest_missing),
    ("external-resource-manifest-invalid-yaml", _manifest_invalid_yaml),
    ("external-resource-manifest-invalid-shape", _manifest_invalid_shape),
    ("external-resource-manifest-duplicate-target", _manifest_duplicate_target),
    ("superpowers-import-skill-name-mismatch", _superpowers_name_mismatch),
    ("broken-local-link", _broken_local_link),
]


def test_catalog_rule_case_inventory_is_explicit() -> None:
    codes = [code for code, _ in CATALOG_RULE_CASES]
    assert len(codes) == len(set(codes))
    assert len(codes) == 47


@pytest.mark.parametrize(
    "code, build_findings",
    CATALOG_RULE_CASES,
    ids=[code for code, _ in CATALOG_RULE_CASES],
)
def test_catalog_rule_reports_non_absence_finding(
    tmp_path: Path, code: str, build_findings: RuleCase
) -> None:
    findings = build_findings(tmp_path)
    matching = [finding for finding in findings if finding.code == code]

    assert matching, f"{code} did not produce its expected finding"
    assert matching[0].path
    assert matching[0].message
