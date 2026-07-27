import json
from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
FIXTURE_PATH = Path(__file__).parent / "fixtures/routing_cases.json"

EXPECTED_DESCRIPTIONS = {
    "internal-java": (
        "Use when editing or reviewing Java source or generic Maven/Gradle "
        "metadata and the main concern is language-level correctness, "
        "readability, dependency intent, compiler release, toolchains, or "
        "focused build validation. Do not use when application architecture "
        "or Spring Boot runtime semantics drive the work."
    ),
    "internal-java-project": (
        "Use when designing or changing framework-neutral Java application or "
        "library structure, domain boundaries, APIs, concurrency, or unit and "
        "contract tests. Do not use when Spring Boot wiring, configuration, "
        "transactions, dependency management, or test contexts determine "
        "correctness."
    ),
    "internal-java-spring-boot-development": (
        "Use when Spring Boot runtime or framework semantics drive work involving "
        "dependency management, bean wiring, configuration, HTTP or data adapters, "
        "scheduling, transactions, test contexts, service connections, or Boot "
        "virtual-thread enablement. Do not use for ordinary Java edits, generic "
        "Maven/Gradle metadata, or framework-neutral application design."
    ),
}

EXPECTED_INTERFACES = {
    "internal-java": {
        "display_name": "Internal Java",
        "short_description": "Java source and build metadata",
        "default_prompt": (
            "Use $internal-java for ordinary Java source or generic Maven/Gradle "
            "metadata work; route project design and Spring Boot semantics to "
            "their dedicated owners."
        ),
    },
    "internal-java-project": {
        "display_name": "Internal Java Project",
        "short_description": "Framework-neutral Java project design",
        "default_prompt": (
            "Use $internal-java-project for framework-neutral Java application or "
            "library design; route Spring Boot runtime semantics to "
            "$internal-java-spring-boot-development."
        ),
    },
    "internal-java-spring-boot-development": {
        "display_name": "Internal Spring Boot",
        "short_description": "Spring Boot runtime and framework semantics",
        "default_prompt": (
            "Use $internal-java-spring-boot-development when Spring Boot wiring, "
            "configuration, transactions, dependency management, or test contexts "
            "determine correctness."
        ),
    },
}

JAVA_SKILL_IDS = tuple(EXPECTED_DESCRIPTIONS)
PROJECT_FORBIDDEN_MARKERS = (
    "@WebMvcTest",
    "@DataJpaTest",
    "@SpringBootTest",
    "@Transactional",
    "@ConfigurationProperties",
    "@ServiceConnection",
    "spring.threads.virtual.enabled",
)
SPRING_REQUIRED_MARKERS = (
    "@ConfigurationProperties",
    "@ServiceConnection",
    "@Transactional",
    "spring.threads.virtual.enabled",
    "references/runtime-semantics.md",
)


def skill_text(skill_id: str) -> str:
    skill_dir = SKILLS_ROOT / skill_id
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(skill_dir.glob("**/*.md"))
    )


def load_frontmatter(skill_id: str) -> dict[str, object]:
    path = SKILLS_ROOT / skill_id / "SKILL.md"
    _, raw_frontmatter, _ = path.read_text(encoding="utf-8").split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def load_interfaces() -> dict[str, dict[str, object]]:
    return {
        skill_id: yaml.safe_load(
            (SKILLS_ROOT / skill_id / "agents/openai.yaml").read_text(
                encoding="utf-8"
            )
        )["interface"]
        for skill_id in JAVA_SKILL_IDS
    }


def load_routing_cases() -> list[dict[str, str]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_internal_java_description_is_exact() -> None:
    assert load_frontmatter("internal-java")["description"] == EXPECTED_DESCRIPTIONS[
        "internal-java"
    ]


def test_internal_java_project_description_is_exact() -> None:
    assert load_frontmatter("internal-java-project")["description"] == EXPECTED_DESCRIPTIONS[
        "internal-java-project"
    ]


def test_internal_java_spring_description_is_exact() -> None:
    assert load_frontmatter("internal-java-spring-boot-development")["description"] == EXPECTED_DESCRIPTIONS[
        "internal-java-spring-boot-development"
    ]


def test_internal_java_interface_is_exact() -> None:
    assert load_interfaces()["internal-java"] == EXPECTED_INTERFACES["internal-java"]


def test_internal_java_project_interface_is_exact() -> None:
    assert load_interfaces()["internal-java-project"] == EXPECTED_INTERFACES[
        "internal-java-project"
    ]


def test_internal_java_spring_interface_is_exact() -> None:
    assert load_interfaces()["internal-java-spring-boot-development"] == EXPECTED_INTERFACES[
        "internal-java-spring-boot-development"
    ]


def test_project_bundle_excludes_spring_runtime_markers() -> None:
    project_text = skill_text("internal-java-project")

    for marker in PROJECT_FORBIDDEN_MARKERS:
        assert marker not in project_text


def test_spring_bundle_owns_framework_markers_and_runtime_reference() -> None:
    spring_text = skill_text("internal-java-spring-boot-development")

    for marker in SPRING_REQUIRED_MARKERS:
        assert marker in spring_text


def test_routing_fixtures_have_unique_ids_and_cover_all_owners() -> None:
    cases = load_routing_cases()
    assert cases
    assert len({case["id"] for case in cases}) == len(cases)
    assert {case["expected_owner"] for case in cases} == {
        *JAVA_SKILL_IDS,
        "none-of-this-family",
    }

    for case in cases:
        assert set(case) == {"id", "prompt", "expected_owner", "reason"}
        assert all(case[field].strip() for field in case)


def test_java_profiles_have_deterministic_skill_membership() -> None:
    profiles = yaml.safe_load(
        (REPO_ROOT / ".github/repo-profiles.yml").read_text(encoding="utf-8")
    )["profiles"]

    assert "skills/internal-java-spring-boot-development/SKILL.md" not in profiles[
        "backend-java"
    ]["recommended_skills"]
    assert profiles["backend-java-spring"]["recommended_skills"] == [
        "skills/internal-java/SKILL.md",
        "skills/internal-java-project/SKILL.md",
        "skills/internal-java-spring-boot-development/SKILL.md",
        "skills/internal-github-actions/SKILL.md",
        "skills/internal-markdown/SKILL.md",
    ]


def test_project_skill_does_not_point_to_removed_examples() -> None:
    project_skill = (SKILLS_ROOT / "internal-java-project/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "references/examples.md" not in project_skill
