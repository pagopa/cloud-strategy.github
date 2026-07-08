from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import yaml

from .shared import (
    Finding,
    finding_sort_key,
    is_imported_asset,
    iter_markdown_assets,
    load_frontmatter,
    normalize_markdown_text,
    read_text,
    significant_text_lines,
)

ROOT_POLICY_MARKERS = ("AGENTS.md", ".github/copilot-instructions.md", ".github/INVENTORY.md")
INVENTORY_LINE_PATTERN = re.compile(r"^- `?\.github/[^`]+`?(?::|\s*$)")
IMPORTED_SKILL_DESCRIPTION_LIMIT = 500
ESTIMATED_TOKEN_BYTES = 4
DELEGATED_REVIEW_PROMPT_PATH = ".github/prompts/internal-review-ai-resources.prompt.md"
DELEGATED_REVIEW_PROMPT_TOKEN_TARGET = 1100
ROOT_ALWAYS_ON_PATHS = ("AGENTS.md",)
ROOT_ALWAYS_ON_TOKEN_TARGET = 4000
COPILOT_REVIEW_PATH = ".github/copilot-instructions.md"
COPILOT_REVIEW_TOKEN_TARGET = 600
REVIEW_BASELINE_PATH = ".github/instructions/copilot-code-review.instructions.md"
REVIEW_BASELINE_CHAR_LIMIT = 4000
REVIEW_BASELINE_REQUIRED_MARKERS = (
    "Critical",
    "Major",
    "Least privilege",
    "no hardcoded secrets",
    "evidenced findings",
)
AGENTS_OPERATIONAL_PROCEDURE_MARKERS = (
    "## Retained Plans",
    "## Retained Learning",
    "01-...md",
    "01-context-and-constraints.md",
    "01-change-summary.md",
    "02-control.md",
    "02-execution.md",
    "questions.md",
    "doubts-and-questions.md",
    "done-*",
    "continue through the remaining numbered plan files",
)


GATEWAY_CORE_SKILL_PATH = ".github/skills/internal-gateway-idea/SKILL.md"
GATEWAY_CORE_BYTE_BUDGET = 16286
GATEWAY_REQUIRED_CONTEXT_BYTE_BUDGET = 30000
GATEWAY_UNIVERSAL_PRELOAD_MARKERS = (
    "Always preload only `grill-me` and `internal-agent-support-next-step`.",
)


def detect_token_risks(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_root_policy_overlap(root))
    findings.extend(check_agents_operational_procedure_markers(root))
    findings.extend(check_root_always_on_budget(root))
    findings.extend(check_copilot_review_budget(root))
    findings.extend(check_delegated_review_prompt_budget(root))
    findings.extend(check_review_baseline_window(root))
    findings.extend(check_inventory_dumps(root))
    findings.extend(check_duplicate_markdown_bodies(root))
    findings.extend(check_imported_skill_description_budget(root))
    findings.extend(check_skill_description_trigger_collisions(root))
    findings.extend(check_internal_agent_skill_list_size(root))
    findings.extend(check_internal_root_policy_overlap(root))
    findings.extend(check_paired_agent_skill_overlap(root))
    findings.extend(check_gateway_core_budget(root))
    findings.extend(check_gateway_universal_preload_regression(root))
    return sorted(findings, key=finding_sort_key)


def estimate_tokens(path: Path) -> int:
    return (len(path.read_bytes()) + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES


def check_root_always_on_budget(root: Path) -> list[Finding]:
    paths = [root / relative_path for relative_path in ROOT_ALWAYS_ON_PATHS]
    if not all(path.exists() for path in paths):
        return []

    estimated_tokens = sum(estimate_tokens(path) for path in paths)
    if estimated_tokens <= ROOT_ALWAYS_ON_TOKEN_TARGET:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="root-always-on-budget",
            path="AGENTS.md",
            message=(
                "AGENTS.md exceeds the canonical always-on "
                f"soft target ({estimated_tokens} estimated tokens, target {ROOT_ALWAYS_ON_TOKEN_TARGET})."
            ),
            suggestion=(
                "Keep AGENTS.md policy-only and move procedural depth to skill owners and references."
            ),
        )
    ]


def check_copilot_review_budget(root: Path) -> list[Finding]:
    path = root / COPILOT_REVIEW_PATH
    if not path.exists():
        return []

    estimated_tokens = estimate_tokens(path)
    if estimated_tokens <= COPILOT_REVIEW_TOKEN_TARGET:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="copilot-review-over-budget",
            path=COPILOT_REVIEW_PATH,
            message=(
                "The Copilot review instructions exceed their compact review budget "
                f"({estimated_tokens} estimated tokens, target {COPILOT_REVIEW_TOKEN_TARGET})."
            ),
            suggestion=(
                "Keep this file review-only and move general policy or procedural detail into AGENTS.md, skills, or owned assets."
            ),
        )
    ]


def check_delegated_review_prompt_budget(root: Path) -> list[Finding]:
    path = root / DELEGATED_REVIEW_PROMPT_PATH
    if not path.exists():
        return []

    estimated_tokens = estimate_tokens(path)
    if estimated_tokens <= DELEGATED_REVIEW_PROMPT_TOKEN_TARGET:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="delegated-review-prompt-budget",
            path=DELEGATED_REVIEW_PROMPT_PATH,
            message=(
                "The delegated AI resource review prompt exceeds its soft token target "
                f"({estimated_tokens} estimated tokens, target {DELEGATED_REVIEW_PROMPT_TOKEN_TARGET})."
            ),
            suggestion=(
                "Keep user inputs and the analysis-only boundary in the prompt, but move reusable workflow "
                "detail into .github/skills/internal-ai-resource-review/."
            ),
        )
    ]


def check_agents_operational_procedure_markers(root: Path) -> list[Finding]:
    path = root / "AGENTS.md"
    if not path.exists():
        return []

    text = read_text(path)
    markers = [
        marker for marker in AGENTS_OPERATIONAL_PROCEDURE_MARKERS if marker in text
    ]
    if not markers:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="agents-operational-procedure-marker",
            path="AGENTS.md",
            message=(
                "AGENTS.md contains operational procedure markers that belong in "
                f"skills or owned files: {', '.join(markers)}."
            ),
            suggestion=(
                "Keep AGENTS.md to stable policy, precedence, ownership boundaries, and "
                "routing anchors; move retained-plan and ledger mechanics to their owners."
            ),
        )
    ]


def check_review_baseline_window(root: Path) -> list[Finding]:
    path = root / REVIEW_BASELINE_PATH
    if not path.exists():
        return []

    window = read_text(path)[:REVIEW_BASELINE_CHAR_LIMIT]
    normalized_window = window.lower()
    missing_markers = [
        marker
        for marker in REVIEW_BASELINE_REQUIRED_MARKERS
        if marker.lower() not in normalized_window
    ]
    if not missing_markers:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="review-baseline-window-missing-core-rules",
            path=REVIEW_BASELINE_PATH,
            message=(
                "The first 4,000 characters of the global review baseline do not carry "
                f"all review-critical anchors: {', '.join(missing_markers)}."
            ),
            suggestion=(
                "Keep severity buckets, security anchors, and evidenced-findings framing inside the first 4,000 characters."
            ),
        )
    ]


def iter_repo_owned_agent_paths(root: Path) -> list[Path]:
    agents_root = root / ".github/agents"
    if not agents_root.exists():
        return []

    return [
        path
        for path in sorted(agents_root.glob("*.agent.md"))
        if path.is_file() and path.name.startswith(("internal-", "local-"))
    ]


def iter_skill_paths(root: Path) -> list[Path]:
    skills_root = root / ".github/skills"
    if not skills_root.exists():
        return []

    return sorted(path for path in skills_root.glob("**/SKILL.md") if path.is_file())


def check_root_policy_overlap(root: Path) -> list[Finding]:
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
            code="root-policy-overlap",
            path="AGENTS.md",
            message=(
                "AGENTS.md and .github/copilot-instructions.md share too many significant lines, "
                f"which increases duplicated context ({len(shared_lines)} overlapping lines)."
            ),
            suggestion="Keep repository-wide agent policy in AGENTS.md and keep .github/copilot-instructions.md review-only.",
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
            if INVENTORY_LINE_PATTERN.match(line.strip())
        ]
        if len(inventory_lines) < 5:
            continue
        findings.append(
            Finding(
                severity="non-blocking",
                code="inventory-dump-in-root-policy",
                path=relative_path,
                message="The file contains inventory-like path dumps that add noise and token cost.",
                suggestion="Keep exact catalog paths in .github/INVENTORY.md instead of repeating them in always-on policy files.",
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
                suggestion="Remove weaker aliases or move shared logic into one canonical file to reduce duplicated context.",
            )
        )
    return findings


def check_imported_skill_description_budget(root: Path) -> list[Finding]:
    profiled_skill_paths = collect_profiled_skill_paths(root)
    findings: list[Finding] = []
    for path in iter_skill_paths(root):
        relative_path = path.relative_to(root).as_posix()
        if not is_imported_asset(relative_path) or relative_path in profiled_skill_paths:
            continue

        description = load_frontmatter(path).get("description")
        if not isinstance(description, str):
            continue

        normalized_description = " ".join(description.split())
        if len(normalized_description) < IMPORTED_SKILL_DESCRIPTION_LIMIT:
            continue

        family = path.parent.name.split("-", maxsplit=1)[0]
        findings.append(
            Finding(
                severity="non-blocking",
                code="imported-skill-description-budget",
                path=relative_path,
                message=(
                    "Imported skill description is long and not referenced by .github/repo-profiles.yml "
                    f"({len(normalized_description)} characters, family `{family}`)."
                ),
                suggestion=(
                    "Keep it support-only, profile-scope it, wrap it only for local routing needs, "
                    "or tighten the description trigger if it creates retrieval ambiguity."
                ),
            )
        )
    return findings


def check_skill_description_trigger_collisions(root: Path) -> list[Finding]:
    paths_by_description: dict[str, list[str]] = defaultdict(list)
    for path in iter_skill_paths(root):
        description = load_frontmatter(path).get("description")
        if not isinstance(description, str):
            continue
        normalized_description = normalize_skill_description_trigger(description)
        if len(normalized_description) < 40:
            continue
        paths_by_description[normalized_description].append(path.relative_to(root).as_posix())

    findings: list[Finding] = []
    for paths in paths_by_description.values():
        if len(paths) < 2:
            continue
        findings.append(
            Finding(
                severity="non-blocking",
                code="skill-description-trigger-collision",
                path=sorted(paths)[0],
                message=(
                    "Multiple skills share the same normalized description trigger: "
                    f"{', '.join(sorted(paths))}."
                ),
                suggestion=(
                    "Make the trigger descriptions distinguish the routing boundary, or consolidate the skills "
                    "if they intentionally describe the same workflow."
                ),
            )
        )
    return findings


def collect_profiled_skill_paths(root: Path) -> set[str]:
    profiles_path = root / ".github/repo-profiles.yml"
    if not profiles_path.exists():
        return set()

    try:
        payload = yaml.safe_load(read_text(profiles_path)) or {}
    except yaml.YAMLError:
        return set()
    if not isinstance(payload, dict):
        return set()

    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        return set()

    profiled_paths: set[str] = set()
    for profile in profiles.values():
        if not isinstance(profile, dict):
            continue
        recommended_skills = profile.get("recommended_skills")
        if not isinstance(recommended_skills, list):
            continue
        for skill_path in recommended_skills:
            if isinstance(skill_path, str):
                profiled_paths.add(normalize_profile_asset_path(skill_path))
    return profiled_paths


def normalize_profile_asset_path(path: str) -> str:
    normalized_path = path.strip().lstrip("/")
    if normalized_path.startswith(".github/"):
        return normalized_path
    if normalized_path.startswith(("agents/", "instructions/", "prompts/", "skills/")):
        return f".github/{normalized_path}"
    return normalized_path


def normalize_skill_description_trigger(description: str) -> str:
    lowered = description.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def check_internal_agent_skill_list_size(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_repo_owned_agent_paths(root):
        bullets = extract_section_bullets(read_text(path), "## Optional Support Skills")
        if len(bullets) > 8:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="large-skill-list",
                    path=path.relative_to(root).as_posix(),
                    message=f"The repo-owned agent declares {len(bullets)} optional support skills, which broadens live context.",
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
            or relative_path.startswith(".github/agents/local-")
            or relative_path.startswith(".github/skills/internal-")
            or relative_path.startswith(".github/skills/local-")
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
                suggestion="Keep repository-wide agent policy in AGENTS.md and reduce the lower-layer asset to local scope.",
            )
        )
    return findings


def check_paired_agent_skill_overlap(root: Path) -> list[Finding]:
    agents_root = root / ".github/agents"
    skills_root = root / ".github/skills"
    if not agents_root.exists() or not skills_root.exists():
        return []

    findings: list[Finding] = []
    for agent_path in iter_repo_owned_agent_paths(root):

        agent_text = read_text(agent_path)
        mandatory_skills = [bullet.strip("`") for bullet in extract_section_bullets(agent_text, "## Mandatory Engine Skills")]
        if not mandatory_skills:
            continue

        frontmatter = load_frontmatter(agent_path)
        agent_name = frontmatter.get("name")
        if not isinstance(agent_name, str) or not agent_name.strip():
            agent_name = agent_path.name.removesuffix(".agent.md")

        if agent_name not in mandatory_skills:
            continue

        skill_path = skills_root / agent_name / "SKILL.md"
        if not skill_path.exists():
            continue

        overlap = {
            line
            for line in significant_text_lines(agent_text) & significant_text_lines(read_text(skill_path))
            if len(line) >= 24
        }
        if len(overlap) < 6:
            continue

        findings.append(
            Finding(
                severity="non-blocking",
                code="paired-agent-skill-overlap",
                path=agent_path.relative_to(root).as_posix(),
                message=(
                    "The agent repeats too much of the paired mandatory skill's guidance, "
                    f"which weakens the engine-skill split ({len(overlap)} overlapping lines)."
                ),
                suggestion="Keep the paired agent boundary-focused and move reusable procedure back into the matching skill.",
            )
        )
    return findings


def check_gateway_core_budget(root: Path) -> list[Finding]:
    path = root / GATEWAY_CORE_SKILL_PATH
    if not path.exists():
        return []

    byte_count = len(path.read_bytes())
    if byte_count <= GATEWAY_CORE_BYTE_BUDGET:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="gateway-core-byte-budget",
            path=GATEWAY_CORE_SKILL_PATH,
            message=(
                "The operational-flow core SKILL.md exceeds its structural byte budget "
                f"({byte_count} bytes, target {GATEWAY_CORE_BYTE_BUDGET})."
            ),
            suggestion=(
                "Compress the core around exclusive reference ownership and phase-local "
                "support loading; do not delete useful lazy depth solely for bundle size."
            ),
        )
    ]


def check_gateway_universal_preload_regression(root: Path) -> list[Finding]:
    path = root / GATEWAY_CORE_SKILL_PATH
    if not path.exists():
        return []

    text = read_text(path)
    found_markers = [
        marker for marker in GATEWAY_UNIVERSAL_PRELOAD_MARKERS if marker in text
    ]
    if not found_markers:
        return []

    return [
        Finding(
            severity="non-blocking",
            code="gateway-universal-preload-regression",
            path=GATEWAY_CORE_SKILL_PATH,
            message=(
                "The operational-flow core still contains universal preload instructions "
                f"that should be phase-local: {', '.join(repr(m) for m in found_markers)}."
            ),
            suggestion=(
                "Load grill-me when Gate 0 activates and internal-agent-support-next-step "
                "when a transition package is needed; do not preload universally."
            ),
        )
    ]


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
