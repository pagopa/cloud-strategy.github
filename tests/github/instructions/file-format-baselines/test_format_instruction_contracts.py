from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def instruction(name: str) -> str:
    return (
        (REPO_ROOT / f".github/instructions/internal-{name}.instructions.md")
        .read_text(encoding="utf-8")
        .lower()
    )


def test_yaml_instruction_covers_format_boundaries_without_domain_cli() -> None:
    text = instruction("yaml")

    for required in (
        "key-duplicates",
        "tabs",
        "anchors/aliases",
        "block scalar/chomping",
        "schema/tag routing",
        "runtime-changing values",
        "environment-scope leaks",
        "secret exposure",
        "domain-policy changes",
    ):
        assert required in text
    assert "aws cloudformation validate-template" not in text


def test_markdown_instruction_separates_structural_and_semantic_review() -> None:
    text = instruction("markdown")

    for required in (
        "md051",
        "md052",
        "md053",
        "fences",
        "local links/fragments",
        "dialect awareness",
        "technical claims",
        "stale references",
        "contradictory guidance",
        "canonical owner",
        "code, tests, or validators",
    ):
        assert required in text
    for excluded in ("prompts", "plans", "governance prose"):
        assert excluded not in text


def test_makefile_instruction_covers_static_rule_and_review_boundaries() -> None:
    text = instruction("makefile")

    for required in (
        "phonydeclared",
        "recipe prefix",
        "$ / $$",
        "order-only prerequisites",
        "parallelism",
        "recursive make",
        "make -n",
        "deterministic build order",
        "hidden environment coupling",
        "failure behavior",
        "undocumented side effects",
    ):
        assert required in text


def test_json_instruction_covers_all_checker_codes_and_interoperability() -> None:
    text = instruction("json")
    body = text.split("---", 2)[-1]

    for required in (
        "json_bom",
        "json_encoding",
        "json_syntax",
        "json_duplicate_key",
        "json_non_finite",
        "json_unsafe_integer",
        "json_number_range",
        "json_unpaired_surrogate",
        "bom/utf-8",
        "duplicate keys",
        "numeric interoperability",
        "object order is not semantic",
        "schema-sensitive key or type changes",
        "required properties",
        "identifiers or enums",
        "secret exposure",
        "contradictory defaults",
    ):
        assert required in text
    assert "registry" not in body
    assert "organization" not in body
