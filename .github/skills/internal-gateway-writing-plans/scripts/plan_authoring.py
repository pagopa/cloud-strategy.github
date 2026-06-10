"""Bundle-local CLI for retained-plan authoring.

Commands: init audit handoff-check tokens
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

COMPACT_REQUIRED_FILES = frozenset(
    {"01-change-summary.md", "02-source-item-ledger.md", "03-execution.md", "questions.md"}
)
EXTENDED_REQUIRED_FILES = COMPACT_REQUIRED_FILES | {"04-implementation-contract.md"}
SUPPORTED_PROFILES = frozenset({"compact", "extended"})
COMPACT_FOLDER_PREFIX = "mini-plan-"
LEDGER_REQUIRED_FIELDS = (
    "Recommended use",
    "Recommended consumer",
    "File map and role",
    "Clarification gate",
    "Initial evidence pass",
    "Reading budget",
    "Target and anti-scope",
    "Owner and validator",
    "Stop conditions",
    "Source item ledger",
)
ITALIAN_SUMMARY_SECTIONS = (
    "Problema da risolvere",
    "Risultato atteso",
    "Risorse coinvolte",
    "Comportamento scelto",
    "Validazione prevista",
    "Esecuzione prevista",
    "Decisione richiesta",
)
RESOURCE_TABLE_HEADER_RE = re.compile(r"\|?\s*Risorsa\s*\|\s*Azione\s*\|\s*Scopo\s*\|?")
PLACEHOLDER_RE = re.compile(r"\b(?:x|tbd|todo|placeholder)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)
EXECUTABLE_STEP_RE = re.compile(r"^\d+\.\s+(.+)$", re.MULTILINE)
GENERIC_TMP_NAMES = frozenset({"plan", "tmp", "test", "misc", "notes", "draft", "new-plan"})
EXTENDED_CONTRACT_SECTIONS = (
    "Sources",
    "Candidate targets",
    "Validation commands",
    "Blockers and fallback rules",
    "External pins",
)


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "ERROR"


def classify_profile(plan_folder: Path) -> str:
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if not ledger_path.is_file():
        return "unsupported"
    text = ledger_path.read_text(encoding="utf-8")
    for profile in SUPPORTED_PROFILES:
        if re.search(rf"Plan profile[:\s]+{profile}", text):
            return profile
    return "unsupported"


def expected_consumer(profile: str) -> str:
    return "internal-gateway-simple-task" if profile == "compact" else "internal-gateway-execute-plans"


def extract_recommended_consumer(ledger_text: str) -> str | None:
    match = re.search(r"Recommended consumer[:\s]+([A-Za-z0-9._-]+)", ledger_text)
    return match.group(1) if match else None


def cmd_init(plan_folder: Path, profile: str = "compact") -> int:
    if plan_folder.exists():
        print(f"ERROR: {plan_folder} already exists", file=sys.stderr)
        return 1

    folder_findings = _validate_folder_name(plan_folder, profile)
    if folder_findings:
        print(f"ERROR: {folder_findings[0].message}", file=sys.stderr)
        return 1

    plan_folder.mkdir(parents=True)
    (plan_folder / "01-change-summary.md").write_text(
        textwrap.dedent(
            """\
            # Sintesi delle modifiche

            ## Problema da risolvere

            TODO

            ## Risultato atteso

            TODO

            ## Risorse coinvolte

            | Risorsa | Azione | Scopo |
            | --- | --- | --- |
            | TBD | TBD | TBD |

            ## Comportamento scelto

            TODO

            ## Validazione prevista

            TODO

            ## Esecuzione prevista

            TODO

            ## Decisione richiesta

            TODO
            """
        ),
        encoding="utf-8",
    )
    ledger_consumer = expected_consumer(profile)
    (plan_folder / "02-source-item-ledger.md").write_text(
        textwrap.dedent(
            f"""\
            # Source Item Ledger

            ## Recommended use

            execute after explicit approval

            ## Recommended consumer

            {ledger_consumer}

            ## Plan profile

            {profile}

            ## File map and role

            | File | Role |
            | --- | --- |
            | `01-change-summary.md` | Italian decision summary; non-executable |
            | `02-source-item-ledger.md` | Authoritative coverage, route, evidence, and stop-condition control |
            | `03-execution.md` | Executable steps |
            | `questions.md` | User-only decisions; excluded from execution |

            ## Clarification gate

            clarification required

            ## Initial evidence pass

            TODO

            ## Reading budget

            TODO

            ## Target and anti-scope

            ### Target

            TODO

            ### Anti-scope

            TODO

            ## Owner and validator

            TODO

            ## Stop conditions

            TODO

            ## Source item ledger

            | ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |
            | --- | --- | --- | --- | --- | --- | --- |
            | TBD-01 | TODO | TODO | repository | TODO | PENDING | `03-execution.md` |
            """
        ),
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text(
        textwrap.dedent(
            """\
            # Execution

            ## Objective

            TODO

            ## Chosen logic

            TODO

            ## Key assumptions

            TODO

            ## Executable steps

            1. Define the first executable step.
               Target: TODO
               Acceptance: TODO
               Validation: TODO
               Fallback: TODO

            ## Validation

            TODO
            """
        ),
        encoding="utf-8",
    )
    if profile == "extended":
        (plan_folder / "04-implementation-contract.md").write_text(
            textwrap.dedent(
                """\
                # Implementation Contract

                ## Sources

                TODO

                ## Candidate targets

                TODO

                ## Validation commands

                TODO

                ## Blockers and fallback rules

                TODO

                ## External pins

                no external evidence
                """
            ),
            encoding="utf-8",
        )
    (plan_folder / "questions.md").write_text("# Questions\n\n- none\n", encoding="utf-8")
    print(f"Created plan folder: {plan_folder}")
    return 0


def _check_unsupported(plan_folder: Path) -> tuple[str | None, list[Finding]]:
    profile = classify_profile(plan_folder)
    if profile == "unsupported":
        return None, [Finding("unsupported-plan-contract", f"Plan folder {plan_folder} has no supported Plan profile (compact or extended)")]
    return profile, []


def _normalize_text(text: str) -> str:
    normalized = text.replace("`", " ")
    normalized = re.sub(r"\|[- :]+\|", " ", normalized)
    normalized = re.sub(r"[^\w\s/-]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _is_placeholder(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized:
        return True
    if PLACEHOLDER_RE.search(normalized):
        return True
    lowered = normalized.lower()
    if lowered in {"-", "none", "n/a"}:
        return True
    return len([token for token in lowered.split() if token not in {"-", "todo", "tbd", "x"}]) == 0


def _section_body(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _subsection_body(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^###\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^###\s+|^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _check_required_section_content(
    findings: list[Finding], text: str, heading: str, *, code_prefix: str
) -> None:
    body = _section_body(text, heading)
    if not body:
        findings.append(Finding(f"{code_prefix}-missing-section", f"Missing section content for: {heading}"))
        return
    if _is_placeholder(body):
        findings.append(Finding(f"{code_prefix}-placeholder", f"Section contains placeholder-only content: {heading}"))


def _validate_folder_name(plan_folder: Path, profile: str) -> list[Finding]:
    parts = plan_folder.parts
    if "tmp" not in parts:
        return []
    folder_name = plan_folder.name.strip().lower()
    if profile == "compact" and not folder_name.startswith(COMPACT_FOLDER_PREFIX):
        return [
            Finding(
                "compact-folder-prefix-required",
                f"Compact retained-plan folders must use mini-plan-*; got {plan_folder.name}",
            )
        ]
    if folder_name in GENERIC_TMP_NAMES:
        return [Finding("unclear-temp-directory-name", f"Temporary plan folder name is too generic: {plan_folder.name}")]
    tokens = [token for token in re.split(r"[-_]+", folder_name) if token]
    if len(tokens) < 2:
        return [Finding("unclear-temp-directory-name", f"Temporary plan folder name must communicate action or context: {plan_folder.name}")]
    return []


def _validate_summary(summary_text: str) -> list[Finding]:
    findings: list[Finding] = []
    for section in ITALIAN_SUMMARY_SECTIONS:
        body = _section_body(summary_text, section)
        if not body:
            findings.append(Finding("missing-summary-section", f"Summary missing Italian section: {section}", "WARNING"))
            continue
        if _is_placeholder(body):
            findings.append(Finding("placeholder-summary-section", f"Summary section contains placeholder-only content: {section}"))
    if not RESOURCE_TABLE_HEADER_RE.search(summary_text):
        findings.append(Finding("missing-resource-table", "Summary missing Risorsa | Azione | Scopo table header", "WARNING"))
    return findings


def _validate_ledger(plan_folder: Path, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if not ledger_path.is_file():
        return [Finding("missing-ledger", "02-source-item-ledger.md is missing")]
    ledger_text = ledger_path.read_text(encoding="utf-8")
    for field in LEDGER_REQUIRED_FIELDS:
        if field not in ledger_text:
            findings.append(Finding("missing-ledger-fields", f"Missing ledger field: {field}"))
    consumer = extract_recommended_consumer(ledger_text)
    if consumer is None:
        findings.append(Finding("missing-recommended-consumer", "Ledger missing Recommended consumer"))
    elif consumer != expected_consumer(profile):
        findings.append(
            Finding(
                "profile-consumer-mismatch",
                f"Profile {profile} requires Recommended consumer: {expected_consumer(profile)}",
            )
        )

    for heading in (
        "Initial evidence pass",
        "Reading budget",
        "Owner and validator",
        "Stop conditions",
        "Source item ledger",
    ):
        _check_required_section_content(findings, ledger_text, heading, code_prefix="ledger")

    target_body = _section_body(ledger_text, "Target and anti-scope")
    if not target_body:
        findings.append(Finding("ledger-missing-section", "Missing section content for: Target and anti-scope"))
    else:
        for subheading in ("Target", "Anti-scope"):
            pattern = re.compile(
                rf"^###\s+{re.escape(subheading)}\s*$([\s\S]*?)(?=^###\s+|^##\s+|\Z)",
                re.MULTILINE,
            )
            match = pattern.search(target_body)
            body = match.group(1).strip() if match else ""
            if not body:
                findings.append(Finding("ledger-missing-subsection", f"Missing subsection content for: {subheading}"))
            elif _is_placeholder(body):
                findings.append(Finding("ledger-placeholder", f"Subsection contains placeholder-only content: {subheading}"))

    source_item_ledger_body = _section_body(ledger_text, "Source item ledger")
    ledger_rows = [
        line
        for line in source_item_ledger_body.splitlines()
        if line.strip().startswith("|")
        and "Source item" not in line
        and "---" not in line
    ]
    if not ledger_rows:
        findings.append(Finding("missing-source-item-coverage", "Source item ledger has no executable coverage rows"))
    else:
        for row in ledger_rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if len(cells) < 7 or any(_is_placeholder(cell) for cell in cells[:6]):
                findings.append(Finding("placeholder-ledger-row", f"Ledger row is incomplete or placeholder-only: {row}"))
                break
    return findings


def _extract_step_blocks(execution_text: str) -> list[tuple[str, str]]:
    body = _section_body(execution_text, "Executable steps")
    if not body:
        return []
    matches = list(EXECUTABLE_STEP_RE.finditer(body))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        blocks.append((match.group(1).strip(), body[start:end].strip()))
    return blocks


def _validate_execution(plan_folder: Path) -> list[Finding]:
    findings: list[Finding] = []
    execution_path = plan_folder / "03-execution.md"
    if not execution_path.is_file():
        return [Finding("missing-execution", "03-execution.md is missing")]
    execution_text = execution_path.read_text(encoding="utf-8")
    for heading in ("Objective", "Chosen logic", "Key assumptions", "Executable steps", "Validation"):
        _check_required_section_content(findings, execution_text, heading, code_prefix="execution")

    step_blocks = _extract_step_blocks(execution_text)
    if not step_blocks:
        findings.append(Finding("missing-executable-steps", "Execution file has no numbered executable steps"))
        return findings

    created_artifacts: dict[str, int] = {}
    consumed_before_create: list[str] = []
    for index, (title, block) in enumerate(step_blocks, start=1):
        if _is_placeholder(title):
            findings.append(Finding("placeholder-step-title", f"Executable step {index} title is placeholder-only"))
        for label in ("Target:", "Acceptance:", "Validation:", "Fallback:"):
            label_match = re.search(rf"{re.escape(label)}\s*(.+)", block)
            if label_match is None:
                findings.append(Finding("incomplete-executable-step", f"Executable step {index} is missing {label.rstrip(':')}"))
                continue
            if _is_placeholder(label_match.group(1)):
                findings.append(Finding("placeholder-executable-step", f"Executable step {index} has placeholder-only {label.rstrip(':')}"))
        create_match = re.search(r"Creates:\s*(.+)", block)
        if create_match:
            created_artifacts[create_match.group(1).strip()] = index
        consume_match = re.search(r"Consumes:\s*(.+)", block)
        if consume_match:
            artifact = consume_match.group(1).strip()
            created_at = created_artifacts.get(artifact)
            if created_at is None:
                consumed_before_create.append(artifact)
    for artifact in consumed_before_create:
        findings.append(Finding("impossible-execution-order", f"Execution consumes artifact before any step creates it: {artifact}"))
    return findings


def _validate_extended_contract(plan_folder: Path) -> list[Finding]:
    findings: list[Finding] = []
    contract_path = plan_folder / "04-implementation-contract.md"
    if not contract_path.is_file():
        return [Finding("missing-implementation-contract", "Extended profile requires 04-implementation-contract.md")]
    contract_text = contract_path.read_text(encoding="utf-8")
    for heading in EXTENDED_CONTRACT_SECTIONS:
        _check_required_section_content(findings, contract_text, heading, code_prefix="implementation-contract")

    external_pins = _section_body(contract_text, "External pins")
    if external_pins and _is_placeholder(external_pins):
        findings.append(Finding("missing-external-evidence-pin", "Extended implementation contract must name an external pin, explicit no-external-evidence statement, or fallback"))
    return findings


def _validate_lower_context_compatibility(plan_folder: Path, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    ledger_text = (plan_folder / "02-source-item-ledger.md").read_text(encoding="utf-8")
    execution_text = (plan_folder / "03-execution.md").read_text(encoding="utf-8")
    summary_text = (plan_folder / "01-change-summary.md").read_text(encoding="utf-8")

    if _is_placeholder(_section_body(summary_text, "Risultato atteso")):
        findings.append(Finding("lower-context-compatible", "Expected outcome is not concrete enough for a lower-context executor"))
    if _is_placeholder(_section_body(ledger_text, "Stop conditions")):
        findings.append(Finding("lower-context-compatible", "Stop conditions are not concrete enough for a lower-context executor"))
    if not _extract_step_blocks(execution_text):
        findings.append(Finding("lower-context-compatible", "Execution file does not show where to start"))
    if profile == "extended":
        contract_text = (plan_folder / "04-implementation-contract.md").read_text(encoding="utf-8")
        if _is_placeholder(_section_body(contract_text, "Candidate targets")):
            findings.append(Finding("lower-context-compatible", "Extended plan does not name concrete candidate targets"))
        if _is_placeholder(_section_body(contract_text, "Validation commands")):
            findings.append(Finding("lower-context-compatible", "Extended plan does not name completion evidence or validation commands"))
    return findings


def _validate(plan_folder: Path, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    required = EXTENDED_REQUIRED_FILES if profile == "extended" else COMPACT_REQUIRED_FILES
    for name in sorted(required):
        if not (plan_folder / name).is_file():
            findings.append(Finding("missing-required-files", f"Missing required file: {name}"))

    findings.extend(_validate_folder_name(plan_folder, profile))

    summary_path = plan_folder / "01-change-summary.md"
    if summary_path.is_file():
        findings.extend(_validate_summary(summary_path.read_text(encoding="utf-8")))
    else:
        findings.append(Finding("missing-summary", "01-change-summary.md is missing"))

    findings.extend(_validate_ledger(plan_folder, profile))
    findings.extend(_validate_execution(plan_folder))
    if profile == "extended":
        findings.extend(_validate_extended_contract(plan_folder))
    return findings


def cmd_audit(plan_folder: Path, format: str = "text") -> int:
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format, warnings=[])
        return 1
    findings.extend(_validate(plan_folder, profile))
    _emit_findings(findings, format, warnings=_token_warnings(plan_folder))
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def cmd_handoff_check(plan_folder: Path, format: str = "text") -> int:
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format, warnings=[])
        return 1
    findings.extend(_validate(plan_folder, profile))
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        if "clarification required" in ledger_text:
            findings.append(Finding("clarification-required", "Clarification gate is still required"))
    if not (plan_folder / "questions.md").is_file():
        findings.append(Finding("missing-questions", "questions.md is missing", "WARNING"))
    findings.extend(_validate_lower_context_compatibility(plan_folder, profile))
    _emit_findings(findings, format, warnings=_token_warnings(plan_folder))
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def _token_warnings(plan_folder: Path) -> list[str]:
    file_tokens: list[tuple[str, int]] = []
    total_tokens = 0
    for md_path in sorted(plan_folder.glob("*.md")):
        tokens = math.ceil(md_path.stat().st_size / 4)
        file_tokens.append((md_path.name, tokens))
        total_tokens += tokens
    warnings: list[str] = []
    control_names = {"01-change-summary.md", "02-source-item-ledger.md", "04-implementation-contract.md"}
    control_tokens = sum(tokens for name, tokens in file_tokens if name in control_names)
    if total_tokens and control_tokens / total_tokens > 0.7:
        warnings.append("Initial control read is disproportionately large; compress or split the control files.")
    for name, tokens in file_tokens:
        if tokens > 1200:
            warnings.append(f"Estimated token weight is high for {name}; split or compress by delivery slice.")
    return warnings


def cmd_tokens(plan_folder: Path, format: str = "text") -> int:
    total_bytes = 0
    file_tokens: list[tuple[str, int]] = []
    for md_path in sorted(plan_folder.glob("*.md")):
        size = md_path.stat().st_size
        total_bytes += size
        tokens = math.ceil(size / 4)
        file_tokens.append((md_path.name, tokens))
    total_tokens = math.ceil(total_bytes / 4)
    warnings = _token_warnings(plan_folder)
    if format == "json":
        json.dump(
            {
                "plan_folder": str(plan_folder),
                "total_tokens_estimate": total_tokens,
                "files": [{"name": name, "tokens": tok} for name, tok in file_tokens],
                "warnings": warnings,
            },
            sys.stdout,
            indent=2,
        )
    else:
        print(f"Plan folder: {plan_folder}")
        print(f"Total estimated tokens: {total_tokens}")
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0


def _emit_findings(findings: list[Finding], format: str, *, warnings: list[str]) -> None:
    if format == "json":
        json.dump(
            {
                "findings": [f.__dict__ for f in findings],
                "warnings": warnings,
                "ready": not any(f.severity == "ERROR" for f in findings),
            },
            sys.stdout,
            indent=2,
        )
    else:
        if findings:
            print("\n".join(f"[{f.severity}] {f.code}: {f.message}" for f in findings))
        else:
            print("No findings.")
        for warning in warnings:
            print(f"[WARNING] token-guidance: {warning}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable retained-plan authoring CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "handoff-check", "tokens"):
        p = sub.add_parser(command)
        p.add_argument("plan_folder", type=Path)
        p.add_argument("--format", choices=("text", "json"), default="text")
    init_p = sub.add_parser("init")
    init_p.add_argument("plan_folder", type=Path)
    init_p.add_argument("--profile", choices=("compact", "extended"), default="compact")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init":
        return cmd_init(args.plan_folder, args.profile)
    if args.command == "audit":
        return cmd_audit(args.plan_folder, args.format)
    if args.command == "handoff-check":
        return cmd_handoff_check(args.plan_folder, args.format)
    if args.command == "tokens":
        return cmd_tokens(args.plan_folder, args.format)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
