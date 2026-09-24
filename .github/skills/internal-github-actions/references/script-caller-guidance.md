# Script Caller Guidance for GitHub Actions

Load this reference when a workflow or composite action calls a script and must forward its output, format, result, or artifacts.

## Contract ownership

The called script owns its selectors and their meaning, execution and lifecycle events, human-readable logs, machine-readable schemas, and exit status. The workflow or action may pass documented selectors and supported format options through. It must not reinterpret script output, invent a parallel schema, or mask the script's status.

The caller owns how supported output reaches the CI consumer. Forward the relevant script output, select a CI format only when the script supports one and a real consumer needs it, and identify the failing step and matrix scope. An explicit supported CI format takes precedence over auto-detection.

Keep CI rendering and artifact handling consumer-led. Use workflow summaries, uploaded artifacts, or other forwarding only when an identified consumer needs them. Preserve the script's documented result paths and avoid duplicate or unsolicited artifacts.

## Compatibility

Treat an existing `--format compact` option, payload, exit code, schema, selector, and caller consumer as public contracts. Forward existing options unchanged and preserve their meaning unless a separately approved migration updates the producer and its consumers together.

A new `--compact` option is a terminal-only projection. It does not replace a CI format or change workflow forwarding, selected work, exit status, machine schemas, or artifacts. Do not route terminal compact output into a CI consumer that expects another format.

## Caller validation boundary

When a change actually modifies workflow, action, selector-forwarding, output, status, schema, or artifact behavior, validate the affected caller contract with workflow or consumer checks. Run `actionlint` when workflow or action files change.

Guidance-only changes do not modify those surfaces. They do not establish that any real CI consumer or validator has exercised this contract.

