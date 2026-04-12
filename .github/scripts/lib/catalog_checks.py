from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .inventory import collect_inventory_sections, parse_inventory_markdown
from .shared import (
    INVENTORY_PATH,
    LEGACY_AGENT_TOOL_IDS,
    Finding,
    finding_sort_key,
    is_local_asset,
    iter_markdown_assets,
    load_frontmatter,
    markdown_link_targets,
    read_text,
    resolve_markdown_target,
)


def run_consistency_checks(root: Path, include_token_risks: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_required_bridge_files(root))
    findings.extend(check_inventory_matches_filesystem(root))
    findings.extend(check_bridge_references(root))
    findings.extend(check_internal_agent_contracts(root))
    findings.extend(check_duplicate_frontmatter_names(root))
    findings.extend(check_source_local_assets(root))
    findings.extend(check_broken_local_links(root))
    if include_token_risks:
        from .token_risks import detect_token_risks

        findings.extend(detect_token_risks(root))
    return sorted(findings, key=finding_sort_key)


def check_required_bridge_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    required_files = ["AGENTS.md", ".github/copilot-instructions.md", INVENTORY_PATH]
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
        if ".github/copilot-instructions.md" not in agents_text:
            findings.append(
                Finding(
                    severity="blocking",
                    code="agents-missing-copilot-reference",
                    path="AGENTS.md",
                    message="AGENTS.md no longer points to .github/copilot-instructions.md as the repo-wide Copilot projection.",
                    suggestion="Restore the reference so the bridge contract remains explicit.",
                )
            )
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
        if "AGENTS.md" not in copilot_text:
            findings.append(
                Finding(
                    severity="blocking",
                    code="copilot-instructions-missing-agents-reference",
                    path=".github/copilot-instructions.md",
                    message=".github/copilot-instructions.md no longer references AGENTS.md as the strategic bridge.",
                    suggestion="Restore the AGENTS.md reference to keep cross-surface precedence explicit.",
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


def check_source_local_assets(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for relative_path in collect_catalog_candidate_paths(root):
        if not is_local_asset(relative_path):
            continue
        findings.append(
            Finding(
                severity="non-blocking",
                code="source-local-asset",
                path=relative_path,
                message="`local-*` assets are reserved for consumer repositories and usually should not live in the standards repository.",
                suggestion="Rename or move the asset if it is intended to be source-managed.",
            )
        )
    return findings


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
        ".github/instructions/internal-*.instructions.md",
        ".github/skills/internal-*/**/*.md",
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
                ".github/instructions/",
                ".github/skills/",
            )
        )
    )
