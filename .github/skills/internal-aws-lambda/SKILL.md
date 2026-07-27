---
name: internal-aws-lambda
description: Use when designing, implementing, refactoring, or reviewing AWS Lambda code, handlers, triggers, packaging, retries, or cold-start behavior after the AWS platform direction is chosen.
disable-model-invocation: true
---

# Internal AWS Lambda

Owns AWS Lambda handler, trigger, packaging, retry, and cold-start behavior after the AWS platform direction is chosen.

If the request falls outside this lane, or routing is unclear under material routing uncertainty, route back to `internal-aws`.

## When to use

- Implementing or reviewing Lambda handlers in Python, Node.js, or TypeScript.
- Designing API Gateway, Function URL, or other HTTP-triggered request/response handling.
- Designing SQS-triggered batch processing, retry, DLQ, or partial-batch-failure flows.
- Packaging, dependency, cold-start, VPC, or runtime-configuration choices specific to Lambda.

## Core guidance

- Keep the handler as a transport adapter; move business logic to testable helpers.
- Code to one event-source contract at a time: HTTP, queue, schedule, or async.
- Parse and validate inputs at the boundary; normalize data passed to business logic.
- Initialize AWS clients outside the handler when reuse is safe; keep imports small.
- Prefer modular SDK clients and narrow dependencies over broad convenience packages.
- Size timeout, memory, concurrency, batch size, and queue visibility timeout as one operating profile.
- Treat duplicate delivery, retries, and idempotency as normal for async triggers.
- Use environment variables for configuration; fetch secrets from managed secret stores.
- Log stable identifiers (request IDs, message IDs); do not log raw sensitive payloads by default.

## Event-source guidance

- **HTTP**: normalize body, path, and query once; return transport-compatible JSON with explicit headers; keep CORS intentional.
- **SQS**: process records independently; handle poison messages explicitly; return only failed item identifiers when partial batch retry is enabled.
- **Scheduled**: make time-window assumptions explicit; guard against duplicate or overlapping execution.
- **File-driven**: avoid recursive triggers by separating input and output prefixes or buckets.

Load `references/examples.md` for minimal handler patterns and event-source checklists.
Load `references/sharp-edges.md` when diagnosing cold starts, VPC latency, retry storms, response-shape mismatches, or file-ingest recursion.
Load `references/common-mistakes.md` for the full mistake table.

## Validation

- Unit tests run outside the Lambda runtime; AWS boundaries are mocked.
- HTTP handlers: malformed body, path, query, and error-response cases tested.
- Queue consumers: duplicate delivery, poison messages, timeout pressure, and partial batch failure tested.
- Code assumptions validated together with deployed timeout, memory, event-source, and queue configuration.
