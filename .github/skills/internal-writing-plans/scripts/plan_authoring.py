"""Bundle-local CLI for retained-plan authoring.

Commands: init audit handoff-check tokens

Stdlib-only. Does not import sibling bundles or .github/scripts/lib.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

COMPACT_REQUIRED_FILES = frozenset(
    {"01-change-summary.md", "02-source-item-ledger.md", "03-execution.md", "questions.md"}
)
EXTENDED_REQUIRED_FILES = COMPACT_REQUIRED_FILES | {"04-implementation-contract.md"}
SUPPORTED_PROFILES = frozenset({"compact", "extended"})

LEDGER_REQUIRED_FIELDS = (
    "Recommended use",
    "File map and role",
    "Clarification gate",
    "Target and anti-scope",
    "Owner and validator",
    "Stop conditions",
)

NUMBERED_FILE_PATTERN = re.compile(r"\d{2}-.+\.md")

ITALIAN_SUMMARY_SECTIONS = (
    "Problema da risolvere",
    "Risultato atteso",
    "Risorse coinvolte",
    "Comportamento scelto",
    "Validazione prevista",
    "Decisione richiesta",
)

RESOURCE_TABLE_HEADER_RE = re.compile(
    r"\|?\s*Risorsa\s*\|\s*Azione\s*\|\s*Scopo\s*\|?"
)


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "ERROR"


def classify_profile(plan_folder: Path) -> str:
    """Classify plan profile. Returns profile name or 'unsupported'."""
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if not ledger_path.is_file():
        return "unsupported"
    text = ledger_path.read_text(encoding="utf-8")
    if re.search(r"Plan profile[:\s]+extended", text):
        return "extended"
    if re.search(r"Plan profile[:\s]+compact", text):
        return "compact"
    return "unsupported"


def cmd_init(plan_folder: Path) -> int:
    """Create a new current-format plan folder."""
    if plan_folder.exists():
        print(f"ERROR: {plan_folder} already exists", file=sys.stderr)
        return 1

    plan_folder.mkdir(parents=True)

    # 01-change-summary.md (Italian)
    summary = textwrap.dedent("""\
        # Sintesi delle modifiche

        ## Problema da risolvere

        - 

        ## Risultato atteso

        - 

        ## Risorse coinvolte

        | Risorsa | Azione | Scopo |
        | --- | --- | --- |
        |  |  |  |

        ## Comportamento scelto

        - 

        ## Validazione prevista

        - 

        ## Decisione richiesta

        - 
    """)
    (plan_folder / "01-change-summary.md").write_text(summary, encoding="utf-8")

    # 02-source-item-ledger.md
    ledger = textwrap.dedent("""\
        # Source Item Ledger

        ## Recommended use

        apply-plan

        ## Plan profile

        compact

        ## File map and role

        | File | Role |
        | --- | --- |
        | `01-change-summary.md` | Italian human-readable decision summary; non-executable |
        | `02-source-item-ledger.md` | Authoritative coverage, route, status, and stop-condition control |
        | `03-execution.md` | Executable steps |
        | `questions.md` | User-only decisions; excluded from execution |

        ## Clarification gate

        clarification required

        ## Initial evidence pass

        1. 

        ## Reading budget

        - 

        ## Target and anti-scope

        ### Target

        - 

        ### Anti-scope

        - 

        ## Owner and validator

        - 

        ## Stop conditions

        - 

        ## Source item ledger

        | ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |
        | --- | --- | --- | --- | --- | --- | --- |
    """)
    (plan_folder / "02-source-item-ledger.md").write_text(ledger, encoding="utf-8")

    # 03-execution.md
    execution = textwrap.dedent("""\
        # Execution

        ## Objective

        ## Chosen logic

        ## Key assumptions

        ## Executable steps

        1. 

        ## Validation

        - 
    """)
    (plan_folder / "03-execution.md").write_text(execution, encoding="utf-8")

    # questions.md
    (plan_folder / "questions.md").write_text("# Questions\n\n- none\n", encoding="utf-8")

    print(f"Created plan folder: {plan_folder}")
    print("01-change-summary.md (Italian), 02-source-item-ledger.md, 03-execution.md, questions.md")
    return 0


def _check_unsupported(plan_folder: Path) -> tuple[str | None, list[Finding]]:
    profile = classify_profile(plan_folder)
    if profile == "unsupported":
        return None, [
            Finding(
                code="unsupported-plan-contract",
                message=f"Plan folder {plan_folder} has no supported Plan profile (compact or extended)",
            )
        ]
    return profile, []


def cmd_audit(plan_folder: Path, format: str = "text") -> int:
    """Validate plan structure against current contract."""
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1

    required = EXTENDED_REQUIRED_FILES if profile == "extended" else COMPACT_REQUIRED_FILES
    for name in sorted(required):
        if not (plan_folder / name).is_file():
            findings.append(
                Finding(code="missing-required-files", message=f"Missing required file: {name}")
            )

    # Ledger validation
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        for field in LEDGER_REQUIRED_FIELDS:
            if field not in ledger_text:
                findings.append(
                    Finding(code="missing-ledger-fields", message=f"Missing ledger field: {field}")
                )

        # Clarification gate
        if "clarification satisfied" in ledger_text:
            pass
        elif "clarification required" in ledger_text:
            pass
        elif "clarification not applicable" in ledger_text:
            pass
        else:
            findings.append(
                Finding(
                    code="clarification-missing",
                    message="Clarification gate status not found in ledger",
                    severity="WARNING",
                )
            )

    # Summary language check
    summary_path = plan_folder / "01-change-summary.md"
    if summary_path.is_file():
        summary_text = summary_path.read_text(encoding="utf-8")
        for section in ITALIAN_SUMMARY_SECTIONS:
            if section not in summary_text:
                findings.append(
                    Finding(
                        code="missing-summary-section",
                        message=f"Summary missing Italian section: {section}",
                        severity="WARNING",
                    )
                )
        if not RESOURCE_TABLE_HEADER_RE.search(summary_text):
            findings.append(
                Finding(
                    code="missing-resource-table",
                    message="Summary missing Risorsa | Azione | Scopo table header",
                    severity="WARNING",
                )
            )

    # Implementation contract
    ic_path = plan_folder / "04-implementation-contract.md"
    if profile == "extended" and not ic_path.is_file():
        findings.append(
            Finding(
                code="missing-implementation-contract",
                message="Extended profile requires 04-implementation-contract.md",
            )
        )

    # Source item ledger rows
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        has_rows = bool(re.search(r"^\| [A-Za-z].*\|.*\|", ledger_text, re.MULTILINE))
        if not has_rows:
            findings.append(
                Finding(
                    code="weak-ledger-coverage",
                    message="Ledger has no source-item rows",
                    severity="WARNING",
                )
            )

    _emit_findings(findings, format)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def cmd_handoff_check(plan_folder: Path, format: str = "text") -> int:
    """Pre-handoff readiness check."""
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1

    # Required files
    required = EXTENDED_REQUIRED_FILES if profile == "extended" else COMPACT_REQUIRED_FILES
    missing_files = [n for n in sorted(required) if not (plan_folder / n).is_file()]
    if missing_files:
        findings.append(
            Finding(
                code="missing-required-files",
                message=f"Missing required files: {', '.join(missing_files)}",
            )
        )

    # Ledger fields
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        missing_fields = [f for f in LEDGER_REQUIRED_FIELDS if f not in ledger_text]
        if missing_fields:
            findings.append(
                Finding(
                    code="missing-ledger-fields",
                    message=f"Missing ledger fields: {', '.join(missing_fields)}",
                )
            )

        # Clarification gate
        if "clarification satisfied" in ledger_text:
            pass
        elif "clarification required" in ledger_text:
            findings.append(
                Finding(code="clarification-required", message="Clarification gate is still required")
            )
        elif "clarification not applicable" in ledger_text:
            pass
        else:
            findings.append(
                Finding(
                    code="clarification-missing",
                    message="Clarification gate status not found in ledger",
                    severity="WARNING",
                )
            )
    else:
        findings.append(Finding(code="missing-ledger", message="02-source-item-ledger.md is missing"))

    # Implementation contract for extended
    ic_path = plan_folder / "04-implementation-contract.md"
    if profile == "extended" and not ic_path.is_file():
        findings.append(
            Finding(
                code="missing-implementation-contract",
                message="Extended profile requires 04-implementation-contract.md",
            )
        )

    # Summary language
    summary_path = plan_folder / "01-change-summary.md"
    if summary_path.is_file():
        summary_text = summary_path.read_text(encoding="utf-8")
        for section in ITALIAN_SUMMARY_SECTIONS:
            if section not in summary_text:
                findings.append(
                    Finding(
                        code="missing-summary-section",
                        message=f"Summary missing Italian section: {section}",
                    )
                )
        if not RESOURCE_TABLE_HEADER_RE.search(summary_text):
            findings.append(
                Finding(
                    code="missing-resource-table",
                    message="Summary missing Risorsa | Azione | Scopo table",
                )
            )
    else:
        findings.append(Finding(code="missing-summary", message="01-change-summary.md is missing"))

    # Questions file
    if not (plan_folder / "questions.md").is_file():
        findings.append(
            Finding(
                code="missing-questions",
                message="questions.md is missing (write '- none' when nothing remains)",
                severity="WARNING",
            )
        )

    # Source-item coverage
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        has_rows = bool(re.search(r"^\| [A-Za-z].*\|.*\|", ledger_text, re.MULTILINE))
        if not has_rows:
            findings.append(
                Finding(
                    code="weak-ledger-coverage",
                    message="Ledger has no source-item rows",
                    severity="WARNING",
                )
            )

    _emit_findings(findings, format)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def cmd_tokens(plan_folder: Path, format: str = "text") -> int:
    """Estimate tokens for plan files."""
    if not plan_folder.is_dir():
        print(f"ERROR: Not a directory: {plan_folder}", file=sys.stderr)
        return 1

    total_bytes = 0
    file_tokens: list[tuple[str, int]] = []
    for md_path in sorted(plan_folder.glob("*.md")):
        size = md_path.stat().st_size
        total_bytes += size
        # Rough estimate: bytes / 4
        tokens = math.ceil(size / 4)
        file_tokens.append((md_path.name, tokens))

    total_tokens = math.ceil(total_bytes / 4)

    if format == "json":
        payload = {
            "plan_folder": str(plan_folder),
            "total_tokens_estimate": total_tokens,
            "files": [{"name": name, "tokens": tok} for name, tok in file_tokens],
        }
        json.dump(payload, sys.stdout, indent=2)
    else:
        print(f"Plan folder: {plan_folder}")
        print(f"Total estimated tokens: {total_tokens}")
        print("Files:")
        for name, tok in file_tokens:
            print(f"  {name}: ~{tok} tokens")
    return 0


def _emit_findings(findings: list[Finding], format: str) -> None:
    if format == "json":
        payload = {
            "findings": [{"code": f.code, "message": f.message, "severity": f.severity} for f in findings],
            "ready": not any(f.severity == "ERROR" for f in findings),
        }
        json.dump(payload, sys.stdout, indent=2)
    else:
        if findings:
            for f in findings:
                print(f"[{f.severity}] {f.code}: {f.message}")
        else:
            print("No findings.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable retained-plan authoring CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create new plan folder")
    init_p.add_argument("plan_folder", type=Path, help="Path to new plan folder")

    audit_p = sub.add_parser("audit", help="Validate plan structure")
    audit_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    audit_p.add_argument("--format", choices=("text", "json"), default="text")

    handoff_p = sub.add_parser("handoff-check", help="Pre-handoff readiness check")
    handoff_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    handoff_p.add_argument("--format", choices=("text", "json"), default="text")

    tokens_p = sub.add_parser("tokens", help="Estimate plan token count")
    tokens_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    tokens_p.add_argument("--format", choices=("text", "json"), default="text")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init":
        return cmd_init(args.plan_folder)
    if args.command == "audit":
        return cmd_audit(args.plan_folder, args.format)
    if args.command == "handoff-check":
        return cmd_handoff_check(args.plan_folder, args.format)
    if args.command == "tokens":
        return cmd_tokens(args.plan_folder, args.format)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
