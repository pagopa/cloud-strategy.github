from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .shared import Finding, finding_sort_key, iter_markdown_assets, normalize_markdown_text, read_text, significant_text_lines


def detect_token_risks(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_bridge_overlap(root))
    findings.extend(check_inventory_dumps(root))
    findings.extend(check_duplicate_markdown_bodies(root))
    findings.extend(check_internal_agent_skill_list_size(root))
    return sorted(findings, key=finding_sort_key)


def check_bridge_overlap(root: Path) -> list[Finding]:
    agents_path = root / "AGENTS.md"
    copilot_path = root / ".github/copilot-instructions.md"
    if not agents_path.exists() or not copilot_path.exists():
        return []

    shared_lines = significant_text_lines(read_text(agents_path)) & significant_text_lines(read_text(copilot_path))
    if len(shared_lines) < 5:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="bridge-overlap",
            path="AGENTS.md",
            message=(
                "AGENTS.md and .github/copilot-instructions.md share too many significant lines, "
                f"which increases prompt duplication ({len(shared_lines)} overlapping lines)."
            ),
            suggestion="Keep strategic bridge rules in AGENTS.md and move repo-wide Copilot behavior to .github/copilot-instructions.md.",
        )
    ]


def check_inventory_dumps(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for relative_path in ["AGENTS.md", ".github/copilot-instructions.md"]:
        path = root / relative_path
        if not path.exists():
            continue
        inventory_lines = [
            line
            for line in read_text(path).splitlines()
            if line.strip().startswith("- ") and ".github/" in line
        ]
        if len(inventory_lines) < 5:
            continue
        findings.append(
            Finding(
                severity="non-blocking",
                code="inventory-dump-in-bridge",
                path=relative_path,
                message="The file contains inventory-like path dumps that add noise and token cost.",
                suggestion="Keep exact catalog paths in .github/INVENTORY.md instead of repeating them in bridge files.",
            )
        )
    return findings


def check_duplicate_markdown_bodies(root: Path) -> list[Finding]:
    normalized_map: dict[str, list[str]] = defaultdict(list)
    for path in iter_markdown_assets(root):
        normalized = normalize_markdown_text(read_text(path))
        if len(normalized) < 200:
            continue
        normalized_map[normalized].append(path.relative_to(root).as_posix())

    findings: list[Finding] = []
    for paths in normalized_map.values():
        if len(paths) < 2:
            continue
        duplicate_paths = ", ".join(sorted(paths))
        findings.append(
            Finding(
                severity="non-blocking",
                code="duplicate-markdown-body",
                path=sorted(paths)[0],
                message=f"Multiple Markdown assets resolve to the same normalized body: {duplicate_paths}.",
                suggestion="Remove weaker aliases or move shared logic into one canonical file to reduce duplicated prompt context.",
            )
        )
    return findings


def check_internal_agent_skill_list_size(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted((root / ".github/agents").glob("internal-*.agent.md")):
        if not path.is_file():
            continue
        bullets = extract_section_bullets(read_text(path), "## Optional Support Skills")
        if len(bullets) > 8:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="large-skill-list",
                    path=path.relative_to(root).as_posix(),
                    message=f"The internal agent declares {len(bullets)} optional support skills, which broadens prompt context.",
                    suggestion="Keep optional skill lists tight and move generic guidance into shared skills when possible.",
                )
            )

        duplicate_bullets = {bullet for bullet in bullets if bullets.count(bullet) > 1}
        for bullet in sorted(duplicate_bullets):
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="duplicate-skill-entry",
                    path=path.relative_to(root).as_posix(),
                    message=f"The optional skill list repeats `{bullet}`.",
                    suggestion="Remove repeated skill entries to keep the contract concise.",
                )
            )
    return findings


def extract_section_bullets(text: str, heading: str) -> list[str]:
    bullets: list[str] = []
    inside_section = False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside_section:
                break
            inside_section = line.strip() == heading
            continue
        if inside_section and line.strip().startswith("- "):
            bullets.append(line.strip()[2:].strip())
    return bullets
