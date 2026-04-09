from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .shared import Finding, finding_sort_key, iter_markdown_assets, normalize_markdown_text, read_text, significant_text_lines

ROOT_POLICY_MARKERS = ("AGENTS.md", ".github/copilot-instructions.md", ".github/INVENTORY.md")


def detect_token_risks(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_bridge_overlap(root))
    findings.extend(check_inventory_dumps(root))
    findings.extend(check_duplicate_markdown_bodies(root))
    findings.extend(check_internal_agent_skill_list_size(root))
    findings.extend(check_internal_root_policy_overlap(root))
    findings.extend(check_instruction_skill_policy_overlap(root))
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


def check_internal_root_policy_overlap(root: Path) -> list[Finding]:
    agents_path = root / "AGENTS.md"
    copilot_path = root / ".github/copilot-instructions.md"
    if not agents_path.exists() or not copilot_path.exists():
        return []

    root_policy_lines = significant_text_lines(read_text(agents_path)) | significant_text_lines(
        read_text(copilot_path)
    )
    findings: list[Finding] = []
    for path in sorted((root / ".github").rglob("*.md")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root).as_posix()
        if not (
            relative_path.startswith(".github/agents/internal-")
            or relative_path.startswith(".github/skills/internal-")
        ):
            continue

        text = read_text(path)
        reference_count = sum(1 for marker in ROOT_POLICY_MARKERS if marker in text)
        if reference_count < 2:
            continue

        overlap = {
            line
            for line in significant_text_lines(text) & root_policy_lines
            if ".github/" not in line and "agents.md" not in line and "inventory.md" not in line
        }
        if len(overlap) < 5:
            continue

        findings.append(
            Finding(
                severity="non-blocking",
                code="internal-root-policy-overlap",
                path=relative_path,
                message=(
                    "The internal asset repeats too much root-governance language while also citing root policy files, "
                    f"which risks turning it into a second policy center ({len(overlap)} overlapping lines)."
                ),
                suggestion="Keep repository-wide bridge policy in AGENTS.md plus .github/copilot-instructions.md and reduce the lower-layer asset to local scope.",
            )
        )
    return findings


def check_instruction_skill_policy_overlap(root: Path) -> list[Finding]:
    instructions_root = root / ".github/instructions"
    skills_root = root / ".github/skills"
    if not instructions_root.exists() or not skills_root.exists():
        return []

    skill_paths = sorted(skills_root.glob("internal-*/SKILL.md"))
    findings: list[Finding] = []
    for instruction_path in sorted(instructions_root.glob("internal-*.instructions.md")):
        topic = instruction_path.name.removesuffix(".instructions.md").removeprefix("internal-")
        instruction_lines = significant_text_lines(read_text(instruction_path))
        if not instruction_lines:
            continue

        for skill_path in skill_paths:
            if topic not in skill_path.parent.name:
                continue

            overlap = significant_text_lines(read_text(skill_path)) & instruction_lines
            if len(overlap) < 3:
                continue

            findings.append(
                Finding(
                    severity="non-blocking",
                    code="instruction-skill-policy-overlap",
                    path=skill_path.relative_to(root).as_posix(),
                    message=(
                        "The internal skill repeats too many instruction-owned policy lines from "
                        f"{instruction_path.relative_to(root).as_posix()} ({len(overlap)} overlapping lines)."
                    ),
                    suggestion="Keep baseline policy in the matching instruction file and narrow the skill to examples, workflow, and specialization.",
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
