---
name: internal-aws-lambda
description: Use when implementing or reviewing an AWS Lambda function contract, including the handler boundary, event source, retries and idempotency, partial batch failure, concurrency, timeouts, packaging, cold starts, or current Lambda limits and runtime support. Route execution-role trust, account, or guardrail design to /internal-aws, and language-only refactoring to the language skill.
---

# Internal AWS Lambda

Own the AWS Lambda function contract: handler boundary, event source,
runtime, packaging, retry, concurrency, cold-start, and configuration
behavior.

## When to use

- Implementing or reviewing Lambda handlers.
- Designing API Gateway, Function URL, or other HTTP-triggered
  request/response handling.
- Designing SQS-triggered batch processing, retry, DLQ, or
  partial-batch-failure flows.
- Packaging, dependency, cold-start, VPC, or runtime-configuration choices
  specific to Lambda.

Hand off other work:

- execution-role trust, cross-account permissions, SCPs, or account
  placement: `/internal-aws`;
- language structure and tests that do not depend on the Lambda contract:
  the language skill, such as `/internal-python-project` or
  `/internal-nodejs-project`;
- Terraform or CloudFormation authoring: `/internal-terraform` or
  `/antigravity-cloudformation-best-practices`.

## Core rules

- Keep the handler as a transport adapter; move business logic to testable
  helpers.
- Code to one event-source contract at a time: HTTP, queue, schedule, or async.
- Parse and validate inputs at the boundary; normalize data passed to business
  logic.
- Initialize AWS clients outside the handler when reuse is safe; keep imports
  small.
- Prefer modular SDK clients and narrow dependencies over broad convenience
  packages.
- Size timeout, memory, concurrency, batch size, and queue visibility timeout
  as one operating profile.
- Treat duplicate delivery, retries, and idempotency as normal for async
  triggers.
- Use environment variables for configuration; fetch secrets from managed
  secret stores.
- Log stable identifiers (request IDs, message IDs); do not log raw sensitive
  payloads by default.
- Attach a function to a VPC only for a concrete private dependency; then
  name its DNS and egress path.

## Event-source guidance

- **HTTP**: normalize body, path, and query once; return transport-compatible
  JSON with explicit headers; keep CORS intentional.
- **SQS**: process records independently; handle poison messages explicitly;
  return only failed item identifiers when partial batch retry is enabled.
- **Scheduled**: make time-window assumptions explicit; guard against duplicate
  or overlapping execution.
- **File-driven**: avoid recursive triggers by separating input and output
  prefixes or buckets.

## Freshness

Timeouts, payload and `/tmp` limits, runtime support, and newer features
change. Verify a number against current AWS documentation before stating
it; otherwise mark it unverified.

Optional enrichment: when AWS Knowledge MCP is available, AWS publishes an
`aws-serverless` agent skill for SnapStart, Powertools, event source
mappings, and current limits. Discover the exact `skill_name` with
`search_documentation` topic `agent_skills`, then load it with
`retrieve_skill`. This skill stays complete without it.

## References

- [references/examples.md](references/examples.md): load for minimal handler
  patterns and event-source checklists.
- [references/sharp-edges.md](references/sharp-edges.md): load when diagnosing
  cold starts, VPC latency, retry storms, duplicate side effects,
  response-shape mismatches, file-ingest recursion, or secret exposure.

## Completion criteria

- Unit tests run outside the Lambda runtime; AWS boundaries are mocked.
- HTTP handlers: malformed body, path, query, and error-response cases tested.
- Queue consumers: duplicate delivery, poison messages, timeout pressure, and
  partial batch failure tested.
- Code assumptions validated together with deployed timeout, memory,
  event-source, and queue configuration.
- Event contract, boundary normalization, retry behavior, and idempotency are
  explicit.
- Numeric limits are sourced or marked unverified.
