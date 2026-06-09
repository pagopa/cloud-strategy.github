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
LEDGER_REQUIRED_FIELDS = (
    "Recommended use",
    "Recommended consumer",
    "File map and role",
    "Clarification gate",
    "Target and anti-scope",
    "Owner and validator",
    "Stop conditions",
)
ITALIAN_SUMMARY_SECTIONS = (
    "Problema da risolvere",
    "Risultato atteso",
    "Risorse coinvolte",
    "Comportamento scelto",
    "Validazione prevista",
    "Decisione richiesta",
)
RESOURCE_TABLE_HEADER_RE = re.compile(r"\|?\s*Risorsa\s*\|\s*Azione\s*\|\s*Scopo\s*\|?")


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


def cmd_init(plan_folder: Path) -> int:
    if plan_folder.exists():
        print(f"ERROR: {plan_folder} already exists", file=sys.stderr)
        return 1

    plan_folder.mkdir(parents=True)
    (plan_folder / "01-change-summary.md").write_text(
        textwrap.dedent(
            """\
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
            """
        ),
        encoding="utf-8",
    )
    (plan_folder / "02-source-item-ledger.md").write_text(
        textwrap.dedent(
            """\
            # Source Item Ledger

            ## Recommended use

            execute after explicit approval

            ## Recommended consumer

            internal-gateway-simple-task

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
            """
        ),
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text(
        textwrap.dedent(
            """\
            # Execution

            ## Objective

            ## Chosen logic

            ## Key assumptions

            ## Executable steps

            1. 

            ## Validation

            - 
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


def _validate(plan_folder: Path, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    required = EXTENDED_REQUIRED_FILES if profile == "extended" else COMPACT_REQUIRED_FILES
    for name in sorted(required):
        if not (plan_folder / name).is_file():
            findings.append(Finding("missing-required-files", f"Missing required file: {name}"))

    ledger_path = plan_folder / "02-source-item-ledger.md"
    if ledger_path.is_file():
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
    else:
        findings.append(Finding("missing-ledger", "02-source-item-ledger.md is missing"))

    summary_path = plan_folder / "01-change-summary.md"
    if summary_path.is_file():
        summary_text = summary_path.read_text(encoding="utf-8")
        for section in ITALIAN_SUMMARY_SECTIONS:
            if section not in summary_text:
                findings.append(Finding("missing-summary-section", f"Summary missing Italian section: {section}", "WARNING"))
        if not RESOURCE_TABLE_HEADER_RE.search(summary_text):
            findings.append(Finding("missing-resource-table", "Summary missing Risorsa | Azione | Scopo table header", "WARNING"))
    else:
        findings.append(Finding("missing-summary", "01-change-summary.md is missing"))

    if profile == "extended" and not (plan_folder / "04-implementation-contract.md").is_file():
        findings.append(Finding("missing-implementation-contract", "Extended profile requires 04-implementation-contract.md"))
    return findings


def cmd_audit(plan_folder: Path, format: str = "text") -> int:
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1
    findings.extend(_validate(plan_folder, profile))
    _emit_findings(findings, format)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def cmd_handoff_check(plan_folder: Path, format: str = "text") -> int:
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1
    findings.extend(_validate(plan_folder, profile))
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        if "clarification required" in ledger_text:
            findings.append(Finding("clarification-required", "Clarification gate is still required"))
    if not (plan_folder / "questions.md").is_file():
        findings.append(Finding("missing-questions", "questions.md is missing", "WARNING"))
    _emit_findings(findings, format)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def cmd_tokens(plan_folder: Path, format: str = "text") -> int:
    total_bytes = 0
    file_tokens: list[tuple[str, int]] = []
    for md_path in sorted(plan_folder.glob("*.md")):
        size = md_path.stat().st_size
        total_bytes += size
        tokens = math.ceil(size / 4)
        file_tokens.append((md_path.name, tokens))
    total_tokens = math.ceil(total_bytes / 4)
    if format == "json":
        json.dump({"plan_folder": str(plan_folder), "total_tokens_estimate": total_tokens, "files": [{"name": name, "tokens": tok} for name, tok in file_tokens]}, sys.stdout, indent=2)
    else:
        print(f"Plan folder: {plan_folder}")
        print(f"Total estimated tokens: {total_tokens}")
    return 0


def _emit_findings(findings: list[Finding], format: str) -> None:
    if format == "json":
        json.dump({"findings": [f.__dict__ for f in findings], "ready": not any(f.severity == "ERROR" for f in findings)}, sys.stdout, indent=2)
    else:
        print("No findings." if not findings else "\n".join(f"[{f.severity}] {f.code}: {f.message}" for f in findings))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable retained-plan authoring CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "handoff-check", "tokens"):
        p = sub.add_parser(command)
        p.add_argument("plan_folder", type=Path)
        p.add_argument("--format", choices=("text", "json"), default="text")
    init_p = sub.add_parser("init")
    init_p.add_argument("plan_folder", type=Path)
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
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
