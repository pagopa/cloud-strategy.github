---
name: local-copilot-log-analyzer
description: Use when analyzing GitHub Copilot Chat debug logs or prompt exports in this repository, especially for low-token diagnosis of token usage, model calls, tool spans, or oversized results.
---

# Local Copilot Log Analyzer

## Referenced skills

- None.

Repository-owned workflow owner for low-token analysis of GitHub Copilot Chat
debug logs and prompt exports in this repository. Route analysis through the
bundle-local `scripts/run.sh` wrapper instead of recreating parser or aggregation
logic in ad-hoc scripts or one-off shell pipelines.

## When to use

- The user wants to inspect Copilot Chat debug logs, prompt exports, token
  usage, model-call counts, tool spans, or oversized result payloads.
- The evidence is already in local files and the goal is to extract bounded
  aggregates before drilling into raw records.
- The task needs a repository-owned workflow for Copilot log analysis rather
  than a change to the analyzer implementation.

## When not to use

- The request is about changing the analyzer implementation itself; edit
  `scripts/analyze_copilot_debug_log/` directly.
- The user already asked for a full raw dump and explicitly accepted the extra
  token and context cost.
- The task cannot be grounded in local debug-log or prompt-export files.

## Workflow

1. Confirm the input kind and path first: `prompt-exports` or `debug-logs`.
2. Use the canonical wrapper, not ad-hoc parsing:
  - `bash scripts/run.sh prompt-exports <file>`
  - `bash scripts/run.sh debug-logs <file> --format markdown`
   - `./.github/scripts/run.sh analyze_copilot_debug_log --help` when the
     wrapper surface is unclear.
3. Start aggregate-first: file size, prompt or token aggregates, model-call
   counts, tool-span counts, result-size summaries, and the smallest targeted
   slices that can prove or disprove the current hypothesis.
4. Prefer the wrapper's bounded `markdown` or `json` output when the input fits
   the tool contract.
5. Avoid full JSON dumps, full prompt bodies, or full log bodies unless the
   user explicitly asks or the exact anomaly cannot be isolated any other way.
6. If the user explicitly asks for deeper output, name the token or context
   impact before expanding and keep the next slice bounded to the missing
   evidence.
7. Preserve the evidence path in the final explanation: input file, wrapper
   command, output format, and the exact aggregate or slice that supported the
   conclusion.

## Measurement And Privacy

- The `debug-logs` command accepts direct `.jsonl` paths as well as existing
  JSON, OTLP, legacy-session, and prompt-export inputs.
- Report cache-read tokens, uncached input tokens, output tokens, and AIU
  separately when present. Treat gross cumulative input as context volume, not
  realized savings.
- Require a before/after run for an optimization claim; otherwise label it as
  an upper bound.
- Keep raw prompt, response, reasoning, user-request, and tool-result bodies
  excluded from output by default.

## Validation

- `bash scripts/run.sh prompt-exports --help`
- `bash scripts/run.sh debug-logs --help`
- `./.github/scripts/run.sh analyze_copilot_debug_log --help`
- `python3 -m pytest .github/skills/local-copilot-log-analyzer/tests/scripts -q`
