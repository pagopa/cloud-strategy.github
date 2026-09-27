from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTOR_ROOT = (
    REPO_ROOT / ".github" / "skills" / "internal-gateway-execute-plans"
)
WRITER_ROOT = REPO_ROOT / ".github" / "skills" / "internal-gateway-writing-plans"
PROTOCOL_PATH = EXECUTOR_ROOT / "references" / "run-protocol.md"
CHAT_TEMPLATES_PATH = EXECUTOR_ROOT / "references" / "chat-templates.md"
TIMESTAMP = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) (.+)$")
TIMESTAMP_GRAMMAR = "<YYYY-MM-DDTHH:MM:SSZ> "

TASK_TWO_MARKERS = (
    "protocol:status",
    "protocol:ledger",
    "protocol:derivation",
    "protocol:stop-codes",
    "protocol:plan-header",
    "protocol:files-globs",
    "example:ledger",
    "example:status",
)

EXPECTED_EVENT_PREFIXES = {
    "START",
    "APPROVAL",
    "CP<n>",
    "Task <N>: started",
    "Task <N>: resumed on partial state",
    "Task <N>: repair",
    "Task <N>: complete",
    "HEAD adopted",
    "Ruling",
    "RESUME",
    "Final review: started",
    "Final: fixed",
    "Final review: done",
    "STOP",
    "END",
}

EXPECTED_STOP_CAUSES = {
    "PLAN_INVALID": {"legacy", "prose-dep", "plan-wrong"},
    "DEPENDS_FAILED": {"<plan>"},
    "NEEDS_CONSENT": {"default-branch", "dirty", "safety"},
    "CHECKOUT_CHANGED": {
        "foreign-commit",
        "foreign-edit",
        "ledger-mismatch",
        "approval-stale",
    },
    "OUT_OF_PERIMETER": {"file", "protected"},
    "TEST_FAILED": {"exhausted"},
    "CHECKPOINT_MISSING": {"<CPn>"},
    "STORAGE_DENIED": {"git-objects", "run-dir"},
}


def extract_block(text: str, marker: str) -> str:
    match = re.search(
        rf"(?m)^<!-- {re.escape(marker)} -->\n```text\n(.*?)\n```$",
        text,
        re.DOTALL,
    )
    assert match is not None, f"missing text block marker: {marker}"
    return match.group(1)


def grammar_regex(line: str) -> re.Pattern[str]:
    parts = re.split(r"(<[^<>]+>)", line)
    pattern = "".join(
        ".+?" if part.startswith("<") and part.endswith(">") else re.escape(part)
        for part in parts
    )
    return re.compile(rf"\A{pattern}\Z")


def protocol_text() -> str:
    return PROTOCOL_PATH.read_text(encoding="utf-8")


def run_protocol_command(
    marker: str, cwd: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    match = re.search(
        rf"(?m)^<!-- {re.escape(marker)} -->\n```sh\n(.*?)\n```$",
        protocol_text(),
        re.DOTALL,
    )
    command = match.group(1) if match is not None else "false"
    return subprocess.run(
        ["sh", "-c", command],
        cwd=cwd,
        env={**os.environ, **env},
        text=True,
        capture_output=True,
        check=False,
    )


def chat_templates_text() -> str:
    assert CHAT_TEMPLATES_PATH.is_file(), "chat-templates.md does not exist"
    return CHAT_TEMPLATES_PATH.read_text(encoding="utf-8")


def writer_block(marker: str) -> str:
    contract_path = WRITER_ROOT / "references" / "plan-contract.md"
    assert contract_path.is_file(), "writer plan-contract.md does not exist"
    return extract_block(contract_path.read_text(encoding="utf-8"), marker)


def ledger_event_grammars() -> list[str]:
    lines = extract_block(protocol_text(), "protocol:ledger").splitlines()
    return [line.removeprefix(TIMESTAMP_GRAMMAR) for line in lines[1:]]


def event_prefix(line: str) -> str:
    for prefix in (
        "Task <N>: resumed on partial state",
        "Task <N>: started",
        "Task <N>: repair",
        "Task <N>: complete",
        "Final review: started",
        "Final review: done",
        "Final: fixed",
        "HEAD adopted",
        "CP<n>",
    ):
        if line.startswith(prefix):
            return prefix
    return line.split(":", maxsplit=1)[0]


def parse_ledger(ledger: list[str]) -> list[tuple[str, str]]:
    events: list[tuple[str, str]] = []
    for line in ledger:
        match = TIMESTAMP.fullmatch(line)
        assert match is not None, f"invalid ledger timestamp: {line}"
        events.append((match.group(1), match.group(2)))
    return events


def derive_status(ledger: list[str]) -> dict[str, str]:
    events = parse_ledger(ledger)
    state = "RUNNING"
    current_task: str | None = None
    completed_tasks: set[str] = set()
    checkpoints: list[tuple[str, str]] = []
    blocker = "none"
    next_action = "none"

    for _, event in events:
        if event.startswith("START:") or event.startswith("RESUME:"):
            state = "RUNNING"
        elif event.startswith("STOP:"):
            state = "BLOCKED"
            stop = re.fullmatch(
                r"STOP: code=(\S+) cause=(\S+) evidence=(.+?) next=(.+)", event
            )
            assert stop is not None, event
            blocker = f"{stop.group(1)}/{stop.group(2)}: {stop.group(3)}"
            next_action = stop.group(4)
        elif event == "END: DONE":
            state = "DONE"
        elif event == "END: PARTIAL":
            state = "PARTIAL"

        started = re.match(r"Task (\d+): started$", event)
        if started:
            current_task = started.group(1)
        completed = re.match(r"Task (\d+): complete(?: |$)", event)
        if completed:
            completed_tasks.add(completed.group(1))
            if current_task == completed.group(1):
                current_task = None

        checkpoint = re.fullmatch(r"CP(\d+): (.+)", event)
        if checkpoint:
            checkpoints.append((checkpoint.group(1), checkpoint.group(2)))

    if state != "BLOCKED":
        blocker = "none"
        next_action = "resume" if state == "PARTIAL" else "none"

    return {
        "State": state,
        "Tasks": f"{len(completed_tasks)}/3",
        "Current": f"Task {current_task} <title>" if current_task else "none",
        "Checkpoint": (
            f"CP{checkpoints[-1][0]} {checkpoints[-1][1]}"
            if checkpoints
            else "none"
        ),
        "Blocker": blocker,
        "Next": next_action,
        "Updated": events[-1][0] if events else "none",
    }


def test_protocol_blocks_are_unique() -> None:
    markers = [
        line[len("<!-- ") : -len(" -->")]
        for line in protocol_text().splitlines()
        if line.startswith("<!-- ") and line.endswith(" -->")
    ]
    selected = [marker for marker in markers if marker in TASK_TWO_MARKERS]

    assert selected == list(TASK_TWO_MARKERS)


def test_status_template_has_nine_labels_in_order() -> None:
    status = extract_block(protocol_text(), "protocol:status")

    assert [line.split(":", maxsplit=1)[0] for line in status.splitlines()] == [
        "Plan",
        "State",
        "Executor",
        "Tasks",
        "Current",
        "Checkpoint",
        "Blocker",
        "Next",
        "Updated",
    ]


def test_status_states_are_the_four_stored_states() -> None:
    status = extract_block(protocol_text(), "protocol:status")
    state_line = next(line for line in status.splitlines() if line.startswith("State:"))

    assert set(state_line.split(": ", maxsplit=1)[1].split("|")) == {
        "RUNNING",
        "PARTIAL",
        "BLOCKED",
        "DONE",
    }


def test_ledger_events_cover_protocol_vocabulary() -> None:
    prefixes = {event_prefix(line) for line in ledger_event_grammars()}

    assert prefixes == EXPECTED_EVENT_PREFIXES


def test_repair_budget_is_two() -> None:
    repair = next(
        line for line in ledger_event_grammars() if line.startswith("Task <N>: repair")
    )

    assert "/2" in repair


def test_stop_codes_have_one_action_per_cause() -> None:
    lines = extract_block(protocol_text(), "protocol:stop-codes").splitlines()
    actions: dict[tuple[str, str], str] = {}
    causes: dict[str, set[str]] = {}

    for line in lines:
        key, action = line.split(" -> ", maxsplit=1)
        code, cause = key.split("/", maxsplit=1)
        assert action.strip()
        assert (code, cause) not in actions
        actions[(code, cause)] = action
        causes.setdefault(code, set()).add(cause)

    assert causes == EXPECTED_STOP_CAUSES
    assert len(actions) == sum(map(len, EXPECTED_STOP_CAUSES.values()))


def test_example_ledger_lines_match_grammar() -> None:
    example = extract_block(protocol_text(), "example:ledger").splitlines()
    grammars = [grammar_regex(line) for line in ledger_event_grammars()]

    for line in example[1:]:
        match = TIMESTAMP.fullmatch(line)
        assert match is not None
        assert any(grammar.fullmatch(match.group(2)) for grammar in grammars), line


def test_example_status_derives_from_example_ledger() -> None:
    example_ledger = extract_block(protocol_text(), "example:ledger").splitlines()[1:]
    example_status = extract_block(protocol_text(), "example:status")
    fields = {
        line.split(":", maxsplit=1)[0]: line.split(": ", maxsplit=1)[1]
        for line in example_status.splitlines()
    }
    derived = derive_status(example_ledger)

    assert fields["State"] == derived["State"]
    assert fields["Tasks"] == derived["Tasks"]
    assert fields["Current"] == derived["Current"]
    assert fields["Checkpoint"] == derived["Checkpoint"]
    assert fields["Blocker"] == derived["Blocker"]
    assert fields["Next"] == derived["Next"]
    assert fields["Updated"] == derived["Updated"]


def test_stored_records_are_emoji_free() -> None:
    emoji = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")

    for marker in (
        "protocol:status",
        "protocol:ledger",
        "protocol:stop-codes",
        "example:ledger",
        "example:status",
    ):
        assert emoji.search(extract_block(protocol_text(), marker)) is None


def test_writer_and_executor_share_plan_header() -> None:
    assert writer_block("protocol:plan-header") == extract_block(
        protocol_text(), "protocol:plan-header"
    )


def test_writer_and_executor_share_files_globs() -> None:
    assert writer_block("protocol:files-globs") == extract_block(
        protocol_text(), "protocol:files-globs"
    )


def test_chat_states_cover_stored_states_with_one_emoji_each() -> None:
    states = extract_block(protocol_text(), "protocol:status")
    state_line = next(line for line in states.splitlines() if line.startswith("State:"))
    stored_states = set(state_line.split(": ", maxsplit=1)[1].split("|"))
    lines = extract_block(chat_templates_text(), "protocol:chat-states").splitlines()
    expected = [
        ("STARTED 🚀", "🚀"),
        ("RUNNING 🔄", "🔄"),
        ("RESUMED 🔁", "🔁"),
        ("PAUSED ⏸️", "⏸️"),
        ("NEEDS CONFIRMATION 🟡", "🟡"),
        ("BLOCKED 🛑", "🛑"),
        ("NOT STARTED 🛑 (preflight)", "🛑"),
        ("NOT STARTED ⚪ (query)", "⚪"),
        ("PLAN TO REWRITE 📜", "📜"),
        ("DONE ✅", "✅"),
    ]
    labels = [line.split(" -> ", maxsplit=1)[0] for line in lines]
    observed_states: set[str] = set()

    assert labels == [label for label, _ in expected]
    for line, (label, emoji) in zip(lines, expected, strict=True):
        right_side = line.split(" -> ", maxsplit=1)[1]
        assert line.count(emoji) == 1
        assert "👉" not in line
        if right_side in stored_states:
            observed_states.add(right_side)

    assert observed_states == stored_states


def test_checkpoint_handles_ignored_scratch_directories(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Plan Test"], cwd=repo, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "plan-test@example.invalid"],
        cwd=repo,
        check=True,
    )
    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    (repo / ".gitignore").write_text("/tmp/\n/.superpowers/\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"], cwd=repo, check=True
    )
    (repo / "tmp").mkdir()
    (repo / ".superpowers").mkdir()
    (repo / "tmp" / "tracked.txt").write_text("scratch\n", encoding="utf-8")
    (repo / ".superpowers" / "tracked.txt").write_text("scratch\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "--force", "tmp/tracked.txt", ".superpowers/tracked.txt"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "track scratch"], cwd=repo, check=True
    )
    (repo / "tmp" / "tracked.txt").write_text("edited scratch\n", encoding="utf-8")
    (repo / ".superpowers" / "tracked.txt").write_text(
        "edited scratch\n", encoding="utf-8"
    )
    run_dir = repo / "tmp" / "run"
    run_dir.mkdir()
    real_index = repo / ".git" / "index"
    index_before = real_index.read_bytes()

    checkpoint = run_protocol_command(
        "cmd:checkpoint", repo, {"RUN_DIR": str(run_dir)}
    )
    assert checkpoint.returncode == 0, checkpoint.stderr
    head_tree = run_protocol_command(
        "cmd:head-tree", repo, {"RUN_DIR": str(run_dir)}
    )
    assert head_tree.returncode == 0, head_tree.stderr

    checkpoint_paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", checkpoint.stdout.strip()],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    head_paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", head_tree.stdout.strip()],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert checkpoint_paths == [".gitignore", "README.md"]
    assert head_paths == checkpoint_paths
    assert real_index.read_bytes() == index_before
