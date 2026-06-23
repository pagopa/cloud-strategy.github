from __future__ import annotations

from collections import defaultdict
import re
from pathlib import Path

import yaml

from .inventory import collect_inventory_sections, parse_inventory_markdown
from .shared import (
    INVENTORY_PATH,
    IMPORTED_ASSET_OVERRIDES_PATH,
    LEGACY_AGENT_TOOL_IDS,
    SUPERPOWERS_NORMALIZATION_PATH,
    Finding,
    finding_sort_key,
    IGNORED_SYNC_FILENAMES,
    IGNORED_SYNC_PARTS,
    is_imported_asset,
    iter_markdown_assets,
    load_frontmatter,
    markdown_link_targets,
    read_text,
    resolve_markdown_target,
)

RESIDUAL_INSTRUCTION_REFERENCE_PATTERNS = (
    (
        re.compile(r"\.github/copilot-code-review-instructions\.md"),
        "retired legacy review instruction path",
    ),
    (
        re.compile(r"\.github/copilot-instructions\.override\.md"),
        "retired override path",
    ),
    (
        re.compile(r"\.github/templates/copilot-instructions\.override\.md\.template"),
        "retired override template path",
    ),
)
SOURCE_INSTRUCTION_REVIEW_MARKER = (
    "optimized for Copilot code review and should produce only evidenced findings"
)


def run_consistency_checks(root: Path, include_token_risks: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_required_bridge_files(root))
    findings.extend(check_inventory_matches_filesystem(root))
    findings.extend(check_bridge_references(root))
    findings.extend(check_internal_agent_contracts(root))
    findings.extend(check_repo_owned_agent_sections(root))
    findings.extend(check_duplicate_frontmatter_names(root))
    findings.extend(check_prompt_contracts(root))
    findings.extend(check_source_instruction_contracts(root))
    findings.extend(check_residual_instruction_family_references(root))
    findings.extend(check_imported_asset_overrides(root))
    findings.extend(check_superpowers_import_naming(root))
    findings.extend(check_broken_local_links(root))
    if include_token_risks:
        from .token_risks import detect_token_risks

        findings.extend(detect_token_risks(root))
    return sorted(findings, key=finding_sort_key)


def check_source_instruction_contracts(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    instructions_root = root / ".github/instructions"
    if not instructions_root.exists():
        return findings

    for path in sorted(instructions_root.rglob("*.instructions.md")):
        relative_path = path.relative_to(root).as_posix()
        frontmatter = load_frontmatter(path)
        description = frontmatter.get("description")
        apply_to = frontmatter.get("applyTo")
        exclude_agent = frontmatter.get("excludeAgent")
        body = read_text(path)

        if not isinstance(description, str) or not description.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="source-instruction-missing-description",
                    path=relative_path,
                    message="Source-managed instructions must declare a non-empty `description:` frontmatter value.",
                    suggestion="Add a short description that frames review checks for the matching paths.",
                )
            )

        if not isinstance(apply_to, str) or not apply_to.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="source-instruction-missing-apply-to",
                    path=relative_path,
                    message="Source-managed instructions must declare a non-empty `applyTo:` frontmatter value.",
                    suggestion="Set `applyTo:` to the narrowest glob that matches the intended review scope.",
                )
            )

        if exclude_agent != "cloud-agent":
            findings.append(
                Finding(
                    severity="blocking",
                    code="source-instruction-missing-exclude-agent",
                    path=relative_path,
                    message="Source-managed instructions must set `excludeAgent: cloud-agent`.",
                    suggestion="Set `excludeAgent: cloud-agent` so this instruction remains review-oriented.",
                )
            )

        if SOURCE_INSTRUCTION_REVIEW_MARKER not in body:
            findings.append(
                Finding(
                    severity="blocking",
                    code="source-instruction-missing-review-statement",
                    path=relative_path,
                    message="Source-managed instructions must include the review-purpose opening statement.",
                    suggestion="Add the common opening statement that this file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.",
                )
            )

        line_count = len(body.splitlines())
        if line_count > 220:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="source-instruction-overgrown",
                    path=relative_path,
                    message=f"Source-managed instruction is overgrown ({line_count} lines) and may behave like a shadow skill.",
                    suggestion="Keep only review-critical checks here and move procedural depth to the matching skill owner.",
                )
            )

    return findings


def check_required_bridge_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    required_files = [
        "AGENTS.md",
        ".github/copilot-instructions.md",
        ".github/instructions/copilot-code-review.instructions.md",
        INVENTORY_PATH,
    ]
    for relative_path in required_files:
        if (root / relative_path).exists():
            continue
        findings.append(
            Finding(
                severity="blocking",
                code="missing-bridge-file",
                path=relative_path,
                message="A required bridge file is missing from the repository.",
                suggestion="Restore the missing governance file before relying on sync or audit automation.",
            )
        )
    return findings


def check_inventory_matches_filesystem(root: Path) -> list[Finding]:
    inventory_path = root / INVENTORY_PATH
    if not inventory_path.exists():
        return []

    expected_sections = collect_inventory_sections(root)
    actual_sections = parse_inventory_markdown(read_text(inventory_path))
    findings: list[Finding] = []
    for section, expected_paths in expected_sections.items():
        expected = set(expected_paths)
        actual = actual_sections.get(section, set())
        missing = sorted(expected - actual)
        stale = sorted(actual - expected)
        for relative_path in missing:
            findings.append(
                Finding(
                    severity="blocking",
                    code="inventory-missing-entry",
                    path=relative_path,
                    message=f"{section} entry exists on disk but is missing from .github/INVENTORY.md.",
                    suggestion="Rebuild .github/INVENTORY.md from the current filesystem state.",
                )
            )
        for relative_path in stale:
            findings.append(
                Finding(
                    severity="blocking",
                    code="inventory-stale-entry",
                    path=relative_path,
                    message=f"{section} entry is listed in .github/INVENTORY.md but missing on disk.",
                    suggestion="Remove stale paths from .github/INVENTORY.md or restore the missing asset.",
                )
            )
    return findings


def check_bridge_references(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_path = root / "AGENTS.md"
    copilot_path = root / ".github/copilot-instructions.md"
    if agents_path.exists():
        agents_text = read_text(agents_path)
        if ".github/INVENTORY.md" not in agents_text:
            findings.append(
                Finding(
                    severity="blocking",
                    code="agents-missing-inventory-reference",
                    path="AGENTS.md",
                    message="AGENTS.md no longer points to .github/INVENTORY.md as the live catalog.",
                    suggestion="Restore the inventory reference in AGENTS.md.",
                )
            )
    if copilot_path.exists():
        copilot_text = read_text(copilot_path)
        if "This file is only for GitHub.com Copilot code review." not in copilot_text:
            findings.append(
                Finding(
                    severity="blocking",
                    code="copilot-instructions-missing-review-scope",
                    path=".github/copilot-instructions.md",
                    message=".github/copilot-instructions.md must explicitly declare GitHub.com code-review-only scope.",
                    suggestion="Restore the review-only scope line in .github/copilot-instructions.md.",
                )
            )

        if (
            "Do not treat this file as instructions for coding agents, local CLIs, or"
            not in copilot_text
        ):
            findings.append(
                Finding(
                    severity="blocking",
                    code="copilot-instructions-missing-runtime-boundary",
                    path=".github/copilot-instructions.md",
                    message=".github/copilot-instructions.md must keep the non-runtime boundary explicit.",
                    suggestion="Restore the non-runtime boundary line under the non-scope section.",
                )
            )
    return findings


def check_internal_agent_contracts(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_root = root / ".github/agents"
    if not agents_root.exists():
        return findings

    for path in sorted(agents_root.glob("internal-*.agent.md")):
        frontmatter = load_frontmatter(path)
        relative_path = path.relative_to(root).as_posix()
        normalized_tools, tools_error = normalize_agent_tools(frontmatter.get("tools"))
        if tools_error in {"missing", "empty"}:
            findings.append(
                Finding(
                    severity="blocking",
                    code="internal-agent-missing-tools",
                    path=relative_path,
                    message="Repository-owned internal agents must declare a non-empty explicit tools contract.",
                    suggestion="Add a `tools:` frontmatter list with the minimum required scope.",
                )
            )
        elif tools_error == "invalid":
            findings.append(
                Finding(
                    severity="blocking",
                    code="internal-agent-invalid-tools",
                    path=relative_path,
                    message="The agent tools contract must be a string or a list of non-empty strings.",
                    suggestion="Normalize `tools:` to a non-empty string or list of non-empty tool ids.",
                )
            )

        legacy_keys = {key for key in frontmatter if key in {"infer", "color"}}
        if legacy_keys:
            findings.append(
                Finding(
                    severity="blocking",
                    code="internal-agent-legacy-frontmatter",
                    path=relative_path,
                    message=f"The agent still declares retired frontmatter keys: {', '.join(sorted(legacy_keys))}.",
                    suggestion="Remove retired keys and keep only supported GitHub Copilot frontmatter fields.",
                )
            )

        for tool_name in normalized_tools:
            if tool_name in LEGACY_AGENT_TOOL_IDS:
                findings.append(
                    Finding(
                        severity="non-blocking",
                        code="internal-agent-legacy-tool-id",
                        path=relative_path,
                        message=f"The tools contract still uses legacy tool id `{tool_name}`.",
                        suggestion="Prefer the canonical GitHub Copilot tool aliases unless a narrower legacy id is still required.",
                    )
                )
    return findings


def check_repo_owned_agent_sections(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_root = root / ".github/agents"
    if not agents_root.exists():
        return findings

    for path in sorted(agents_root.glob("*.agent.md")):
        if not path.is_file() or not path.name.startswith(("internal-", "local-")):
            continue

        relative_path = path.relative_to(root).as_posix()
        text = read_text(path)

        if "## Preferred/Optional Skills" in text:
            findings.append(
                Finding(
                    severity="blocking",
                    code="repo-owned-agent-legacy-skill-heading",
                    path=relative_path,
                    message=(
                        "Repository-owned agents must use `## Optional Support Skills` instead of the legacy "
                        "`## Preferred/Optional Skills` heading."
                    ),
                    suggestion=(
                        "Replace the legacy heading and keep `## Skill Usage Contract` only when support "
                        "skills are genuinely conditional."
                    ),
                )
            )

        if "## Skill Usage Contract" in text and "## Optional Support Skills" not in text:
            findings.append(
                Finding(
                    severity="blocking",
                    code="repo-owned-agent-skill-usage-without-optional-support",
                    path=relative_path,
                    message=(
                        "Repository-owned agents should not keep `## Skill Usage Contract` without an "
                        "`## Optional Support Skills` section."
                    ),
                    suggestion=(
                        "Remove `## Skill Usage Contract` or add `## Optional Support Skills` only when the "
                        "declared skills are genuinely conditional."
                    ),
                )
            )

    return findings


def check_duplicate_frontmatter_names(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    groups = {
        "agent": sorted((root / ".github/agents").glob("*.agent.md")),
        "skill": sorted((root / ".github/skills").glob("**/SKILL.md")),
    }
    for family, paths in groups.items():
        names: dict[str, list[str]] = defaultdict(list)
        for path in paths:
            if not path.is_file():
                continue
            name = load_frontmatter(path).get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            names[name.strip()].append(path.relative_to(root).as_posix())
        for name, duplicate_paths in sorted(names.items()):
            if len(duplicate_paths) < 2:
                continue
            findings.append(
                Finding(
                    severity="blocking",
                    code="duplicate-frontmatter-name",
                    path=duplicate_paths[0],
                    message=f"The {family} name `{name}` is declared more than once: {', '.join(duplicate_paths)}.",
                    suggestion="Keep one canonical asset name per family to avoid ambiguous matching and routing.",
                )
            )
    return findings


def check_prompt_contracts(root: Path) -> list[Finding]:
    prompts_root = root / ".github/prompts"
    if not prompts_root.exists():
        return []

    findings: list[Finding] = []
    for path in sorted(prompts_root.glob("*.prompt.md")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root).as_posix()
        frontmatter = load_frontmatter(path)
        expected_name = path.name.removesuffix(".prompt.md")

        name = frontmatter.get("name")
        if not isinstance(name, str) or not name.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="prompt-missing-name",
                    path=relative_path,
                    message="Prompt files must declare a non-empty `name:` frontmatter value.",
                    suggestion="Set `name:` to the canonical prompt identifier so catalog routing stays explicit.",
                )
            )
        elif name.strip() != expected_name:
            findings.append(
                Finding(
                    severity="blocking",
                    code="prompt-name-mismatch",
                    path=relative_path,
                    message=(
                        f"Prompt frontmatter name `{name.strip()}` does not match the filename stem `{expected_name}`."
                    ),
                    suggestion="Keep prompt filename and `name:` aligned so prompt routing stays deterministic.",
                )
            )

        agent = frontmatter.get("agent")
        if not isinstance(agent, str) or not agent.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="prompt-missing-agent",
                    path=relative_path,
                    message="Prompt files must declare a non-empty `agent:` frontmatter value.",
                    suggestion="Declare the intended agent owner so prompt entrypoint behavior stays reviewable.",
                )
            )
        elif agent.strip() == "agent":
            findings.append(
                Finding(
                    severity="blocking",
                    code="prompt-generic-agent",
                    path=relative_path,
                    message="Prompt files must declare a concrete agent owner, not the generic `agent` placeholder.",
                    suggestion="Point the prompt at the intended visible wrapper or sync owner.",
                )
            )

        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="prompt-missing-description",
                    path=relative_path,
                    message="Prompt files must declare a non-empty `description:` frontmatter value.",
                    suggestion="Add a short description that explains when the prompt should be used.",
                )
            )

        if "${input:" not in read_text(path):
            findings.append(
                Finding(
                    severity="blocking",
                    code="prompt-missing-input-placeholder",
                    path=relative_path,
                    message="Prompt files must expose at least one `${input:...}` placeholder for reusable invocation.",
                    suggestion="Add one or more `${input:...}` placeholders so the prompt can collect structured operator input.",
                )
            )

    return findings


def check_residual_instruction_family_references(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_markdown_assets(root):
        relative_path = path.relative_to(root).as_posix()
        if (
            relative_path == INVENTORY_PATH
            or relative_path == ".github/CHANGELOG.md"
            or relative_path == ".github/DEPRECATION.md"
            or relative_path.startswith(".github/instructions/")
        ):
            continue

        text = read_text(path)
        for pattern, label in RESIDUAL_INSTRUCTION_REFERENCE_PATTERNS:
            if not pattern.search(text):
                continue
            findings.append(
                Finding(
                    severity="blocking",
                    code="residual-instruction-reference",
                    path=relative_path,
                    message=f"Active Markdown still references a retired instruction asset via {label}.",
                    suggestion="Route the rule to the smallest valid owner and remove legacy-path references from active contracts.",
                )
            )
            break
    return findings


def normalize_agent_tools(tools: object) -> tuple[list[str], str | None]:
    if tools is None:
        return [], "missing"

    if isinstance(tools, str):
        normalized = tools.strip()
        if not normalized:
            return [], "empty"
        return [normalized], None

    if not isinstance(tools, list):
        return [], "invalid"

    if not tools:
        return [], "empty"

    normalized_tools: list[str] = []
    for tool in tools:
        if not isinstance(tool, str):
            return [], "invalid"
        normalized = tool.strip()
        if not normalized:
            return [], "invalid"
        normalized_tools.append(normalized)
    return normalized_tools, None


def check_imported_asset_overrides(root: Path) -> list[Finding]:
    registry_path = root / IMPORTED_ASSET_OVERRIDES_PATH
    if not registry_path.exists():
        return []

    try:
        payload = yaml.safe_load(read_text(registry_path)) or {}
    except yaml.YAMLError as error:
        return [
            Finding(
                severity="blocking",
                code="imported-asset-overrides-invalid-yaml",
                path=IMPORTED_ASSET_OVERRIDES_PATH,
                message=f"The imported-asset override registry is not valid YAML: {error}.",
                suggestion="Fix the YAML syntax so approved imported overrides remain auditable.",
            )
        ]

    overrides = payload.get("overrides")
    if not isinstance(overrides, list):
        return [
            Finding(
                severity="blocking",
                code="imported-asset-overrides-missing-list",
                path=IMPORTED_ASSET_OVERRIDES_PATH,
                message="The imported-asset override registry must define an `overrides` list.",
                suggestion="Add an `overrides` list or remove the registry until an approved override exists.",
            )
        ]

    findings: list[Finding] = []
    ids_seen: set[str] = set()
    targets_seen: set[str] = set()
    skill_root = registry_path.parent.parent
    for entry in overrides:
        if not isinstance(entry, dict):
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-invalid-entry",
                    path=IMPORTED_ASSET_OVERRIDES_PATH,
                    message="Each imported-asset override entry must be a mapping.",
                    suggestion="Normalize the registry entries to YAML mappings.",
                )
            )
            continue

        override_id = entry.get("id")
        target_path = entry.get("target_path")
        patch_path = entry.get("patch_path")
        expected_hash = entry.get("expected_content_hash")
        approval = entry.get("approval")
        lifecycle_mode = entry.get("lifecycle_mode")
        apply_strategy = entry.get("apply_strategy")

        if not isinstance(override_id, str) or not override_id.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-missing-id",
                    path=IMPORTED_ASSET_OVERRIDES_PATH,
                    message="An imported-asset override entry is missing a non-empty `id`.",
                    suggestion="Give every override a stable id so sync replay can target it explicitly.",
                )
            )
        elif override_id in ids_seen:
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-duplicate-id",
                    path=IMPORTED_ASSET_OVERRIDES_PATH,
                    message=f"The imported-asset override id `{override_id}` is declared more than once.",
                    suggestion="Keep one unique registry entry per approved imported override.",
                )
            )
        else:
            ids_seen.add(override_id)

        if not isinstance(target_path, str) or not target_path.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-missing-target",
                    path=IMPORTED_ASSET_OVERRIDES_PATH,
                    message="An imported-asset override entry is missing `target_path`.",
                    suggestion="Point each override at the imported asset it patches.",
                )
            )
            continue

        if target_path in targets_seen:
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-duplicate-target",
                    path=target_path,
                    message="The imported-asset override registry maps the same target more than once.",
                    suggestion="Keep one canonical override entry per imported target path.",
                )
            )
        else:
            targets_seen.add(target_path)

        if not is_imported_asset(target_path):
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-target-not-imported",
                    path=target_path,
                    message="Imported-asset override targets must point to non-internal, non-local catalog assets.",
                    suggestion="Move repository-owned behavior into an internal asset instead of registering it as an imported override.",
                )
            )
            continue

        target_file = root / target_path
        if not target_file.exists():
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-target-missing",
                    path=target_path,
                    message="The imported-asset override target does not exist on disk.",
                    suggestion="Restore the target asset or remove the stale override entry.",
                )
            )
            continue

        if approval != "explicit-user-counter-validated":
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-approval-missing",
                    path=target_path,
                    message="Imported-asset overrides require `approval: explicit-user-counter-validated`.",
                    suggestion="Record the explicit user counter-validation before keeping the override active.",
                )
            )

        if lifecycle_mode != "post-refresh-patch":
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-invalid-lifecycle",
                    path=target_path,
                    message="Imported-asset overrides must use `lifecycle_mode: post-refresh-patch`.",
                    suggestion="Keep the override replay model explicit instead of inventing ad hoc lifecycle states.",
                )
            )

        if apply_strategy not in {"git-apply", "git-apply-3way"}:
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-invalid-apply-strategy",
                    path=target_path,
                    message=(
                        "Imported-asset overrides must declare `apply_strategy` as "
                        "`git-apply` or `git-apply-3way`."
                    ),
                    suggestion=(
                        "Keep the replay mechanism explicit so upstream-refresh "
                        "behavior stays auditable and repeatable."
                    ),
                )
            )

        if not isinstance(patch_path, str) or not patch_path.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-missing-patch",
                    path=target_path,
                    message="Imported-asset overrides must declare a replay patch path.",
                    suggestion="Add a patch file under the local-agent-sync-external-resources skill bundle.",
                )
            )
        else:
            patch_file = skill_root / patch_path
            if not patch_file.exists():
                findings.append(
                    Finding(
                        severity="blocking",
                        code="imported-asset-override-patch-missing",
                        path=patch_file.relative_to(root).as_posix()
                        if patch_file.is_relative_to(root)
                        else patch_path,
                        message="The replay patch declared for an imported override is missing on disk.",
                        suggestion="Restore the patch file or remove the stale override entry.",
                    )
                )

        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            findings.append(
                Finding(
                    severity="blocking",
                    code="imported-asset-override-invalid-hash",
                    path=target_path,
                    message="Imported-asset overrides must declare a 64-character expected content hash.",
                    suggestion="Store the normalized content hash so validator and replay can detect drift.",
                )
            )
        else:
            from .fingerprinting import build_fingerprint

            actual_hash = build_fingerprint(root, target_file).content_hash
            if actual_hash != expected_hash:
                findings.append(
                    Finding(
                        severity="blocking",
                        code="imported-asset-override-hash-mismatch",
                        path=target_path,
                        message="The imported-asset override target no longer matches the registry hash.",
                        suggestion="Refresh the registry and replay patch together, or revert the untracked drift.",
                    )
                )

    return findings


def check_superpowers_import_naming(root: Path) -> list[Finding]:
    config_path = root / SUPERPOWERS_NORMALIZATION_PATH
    if not config_path.exists():
        return [
            Finding(
                severity="blocking",
                code="superpowers-normalization-reference-missing",
                path=SUPERPOWERS_NORMALIZATION_PATH,
                message="The obra/superpowers import normalization reference is missing.",
                suggestion="Restore the reference so sync refreshes and catalog validation share one naming map.",
            )
        ]

    try:
        payload = yaml.safe_load(read_text(config_path)) or {}
    except yaml.YAMLError as error:
        return [
            Finding(
                severity="blocking",
                code="superpowers-normalization-reference-invalid-yaml",
                path=SUPERPOWERS_NORMALIZATION_PATH,
                message=f"The obra/superpowers normalization reference is not valid YAML: {error}.",
                suggestion="Fix the YAML syntax before relying on sync normalization.",
            )
        ]

    managed_skills = normalize_superpowers_managed_skills(payload)
    if not managed_skills:
        return [
            Finding(
                severity="blocking",
                code="superpowers-normalization-reference-empty",
                path=SUPERPOWERS_NORMALIZATION_PATH,
                message="The obra/superpowers normalization reference does not declare managed skills.",
                suggestion="Add the managed skill map from the retained migration plan.",
            )
        ]

    findings: list[Finding] = []
    for entry in managed_skills:
        legacy_local = entry["legacy_local"]
        local = entry["local"]
        legacy_directory = root / ".github/skills" / legacy_local
        if legacy_directory.exists():
            findings.append(
                Finding(
                    severity="blocking",
                    code="superpowers-import-legacy-skill-directory",
                    path=legacy_directory.relative_to(root).as_posix(),
                    message="A managed obra/superpowers skill still uses the retired `obra-*` directory name.",
                    suggestion=f"Rename the skill directory to `.github/skills/{local}`.",
                )
            )

        for skill_file in (legacy_directory / "SKILL.md", root / ".github/skills" / local / "SKILL.md"):
            if not skill_file.exists():
                continue
            skill_name = load_frontmatter(skill_file).get("name")
            if skill_name == local:
                continue
            findings.append(
                Finding(
                    severity="blocking",
                    code="superpowers-import-skill-name-mismatch",
                    path=skill_file.relative_to(root).as_posix(),
                    message="A managed obra/superpowers skill frontmatter name does not match its canonical local id.",
                    suggestion=f"Set `name: {local}` so the skill id matches the directory name.",
                )
            )

    findings.extend(check_superpowers_legacy_references(root, payload, managed_skills))
    return findings


def normalize_superpowers_managed_skills(payload: dict[str, object]) -> list[dict[str, str]]:
    raw_entries = payload.get("managed_skills")
    if not isinstance(raw_entries, list):
        return []

    normalized_entries: list[dict[str, str]] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            continue
        upstream = raw_entry.get("upstream")
        legacy_local = raw_entry.get("legacy_local")
        local = raw_entry.get("local")
        if not all(isinstance(value, str) and value.strip() for value in (upstream, legacy_local, local)):
            continue
        normalized_entries.append(
            {
                "upstream": upstream.strip(),
                "legacy_local": legacy_local.strip(),
                "local": local.strip(),
            }
        )
    return normalized_entries


def check_superpowers_legacy_references(
    root: Path,
    payload: dict[str, object],
    managed_skills: list[dict[str, str]],
) -> list[Finding]:
    findings: list[Finding] = []
    legacy_tokens = {entry["legacy_local"] for entry in managed_skills}
    upstream_reference_tokens = {
        f"superpowers:{entry['upstream']}": entry["local"] for entry in managed_skills
    }

    for relative_path in collect_superpowers_scan_paths(root, payload):
        text = read_text(root / relative_path)
        for legacy_token in sorted(legacy_tokens):
            if legacy_token not in text:
                continue
            findings.append(
                Finding(
                    severity="blocking",
                    code="superpowers-import-legacy-reference",
                    path=relative_path,
                    message=f"A live catalog asset still references retired local id `{legacy_token}`.",
                    suggestion="Replace managed obra/superpowers ids with the canonical `superpowers-*` ids.",
                )
            )

        for upstream_token, local in sorted(upstream_reference_tokens.items()):
            if upstream_token not in text:
                continue
            findings.append(
                Finding(
                    severity="blocking",
                    code="superpowers-import-upstream-reference",
                    path=relative_path,
                    message=f"A live catalog asset still references upstream skill id `{upstream_token}`.",
                    suggestion=f"Use the canonical local id `{local}` instead.",
                )
            )

    return findings


def collect_superpowers_scan_paths(root: Path, payload: dict[str, object]) -> list[str]:
    live_scan = payload.get("live_scan") if isinstance(payload.get("live_scan"), dict) else {}
    raw_includes = live_scan.get("include") if isinstance(live_scan, dict) else None
    includes = raw_includes if isinstance(raw_includes, list) else []
    ignored_files = set(IGNORED_SYNC_FILENAMES)
    raw_ignored_files = live_scan.get("ignored_files") if isinstance(live_scan, dict) else None
    if isinstance(raw_ignored_files, list):
        ignored_files.update(item for item in raw_ignored_files if isinstance(item, str))

    paths: set[str] = set()
    for include in includes:
        if not isinstance(include, str) or not include.strip():
            continue
        candidate = root / include
        if candidate.is_file() and should_scan_superpowers_path(root, candidate, ignored_files):
            paths.add(candidate.relative_to(root).as_posix())
            continue
        if not candidate.is_dir():
            continue
        for child in candidate.rglob("*"):
            if child.is_file() and should_scan_superpowers_path(root, child, ignored_files):
                paths.add(child.relative_to(root).as_posix())

    return sorted(paths)


def should_scan_superpowers_path(root: Path, path: Path, ignored_files: set[str]) -> bool:
    relative_path = path.relative_to(root).as_posix()
    if path.name in ignored_files:
        return False
    if any(part in IGNORED_SYNC_PARTS for part in path.relative_to(root).parts):
        return False
    if relative_path.startswith("tmp/"):
        return False
    return path.suffix in {".md", ".yaml", ".yml", ".json", ".jsonc", ".py", ".patch"}


def check_broken_local_links(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in collect_repository_owned_markdown_paths(root):
        text = read_text(path)
        for target in markdown_link_targets(text):
            resolved = resolve_markdown_target(root, path, target)
            if resolved is None:
                continue
            if resolved.exists():
                continue
            findings.append(
                Finding(
                    severity="blocking",
                    code="broken-local-link",
                    path=path.relative_to(root).as_posix(),
                    message=f"The Markdown file links to a missing local path: {target}.",
                    suggestion="Fix the target path or restore the referenced file.",
                )
            )
    return findings


def collect_repository_owned_markdown_paths(root: Path) -> list[Path]:
    owned_paths: list[Path] = []
    candidate_patterns = [
        "AGENTS.md",
        ".github/copilot-instructions.md",
        ".github/agents/internal-*.agent.md",
        ".github/agents/local-*.agent.md",
        ".github/prompts/*.prompt.md",
        ".github/skills/internal-*/**/*.md",
        ".github/skills/local-*/**/*.md",
    ]
    for pattern in candidate_patterns:
        owned_paths.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(owned_paths))


def collect_catalog_candidate_paths(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in (root / ".github").rglob("*")
        if path.is_file()
        and path.relative_to(root).as_posix().startswith(
            (
                ".github/agents/",
                ".github/prompts/",
                ".github/skills/",
            )
        )
    )
