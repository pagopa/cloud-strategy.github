---
name: internal-aws-lambda
description: Use when designing, implementing, refactoring, or reviewing AWS Lambda code, handlers, triggers, packaging, retries, or cold-start behavior after the AWS platform direction is chosen.
---

# Internal AWS Lambda

## Referenced skills

- `internal-aws-strategic`: AWS direction or tradeoff questions before implementation.
- `internal-aws-governance`: IAM, trust, queue policy, and guardrail design around Lambda.
- `internal-aws-operations`: rollout validation, monitoring, evidence, recovery, and operational proof.
- `internal-python`: shared Python baseline for Python Lambda code.
- `internal-nodejs`: shared JavaScript, Node.js, and TypeScript baseline for Lambda code.
- `internal-python-project`: structured Python modules used by Lambda handlers.
- `internal-nodejs-project`: structured Node.js or TypeScript modules used by Lambda handlers.
- `internal-terraform`: Terraform infrastructure for Lambda resources.

## When to use

- Implementing or reviewing AWS Lambda handlers in Python, Node.js, or TypeScript.
- Designing API Gateway, Lambda Function URL, or other HTTP-triggered request and response handling.
- Designing SQS-triggered batch processing, retry behavior, DLQ handling, or partial batch failure flows.
- Making packaging, dependency, cold-start, VPC, or runtime-configuration choices that are specific to AWS Lambda behavior.

## When not to use

- The main problem is still strategic AWS decision support rather than implementation.
- The main problem is IAM, SCP, trust, or organization-structure design.
- The next need is operational evidence, rollout validation, monitoring posture, or DR validation rather than handler design.
- The task is generic Python or Node.js module design with no AWS Lambda behavior in scope.

## Core guidance

- Keep the Lambda handler as a transport adapter; move business logic to testable helpers or services.
- Make the event source explicit and code to one contract at a time: HTTP, queue, schedule, or another async trigger.
- Parse and validate inputs at the boundary, then normalize the data passed to business logic.
- Initialize AWS clients outside the handler when reuse is safe, but keep imports and dependencies small.
- Prefer modular AWS SDK clients and narrow dependencies over broad convenience packages.
- Size timeout, memory, concurrency, batch size, and queue visibility timeout as one operating profile instead of independent toggles.
- Treat duplicate delivery, retries, and idempotency as normal behavior for asynchronous triggers.
- Use environment variables for configuration only; fetch secrets from managed secret stores.
- Log stable identifiers such as request IDs and message IDs, but do not log raw sensitive payloads by default.

## Event-source guidance

- **HTTP**: Normalize body, path, and query parsing once; return transport-compatible JSON responses with explicit headers; keep CORS intentional.
- **SQS**: Process records independently, handle poison messages explicitly, and return only failed item identifiers when partial batch retry is enabled.
- **Scheduled events**: Make time-window assumptions explicit and guard against duplicate or overlapping execution.
- **File-driven workflows**: Avoid recursive triggers by separating input and output prefixes or buckets.

Load `references/examples.md` when you need minimal AWS-specific handler patterns or event-source checklists.

Load `references/sharp-edges.md` when diagnosing cold starts, VPC latency, retry storms, response-shape mismatches, or file-ingest recursion.

## Relationship to adjacent skills

- Use `internal-aws-strategic` when the AWS direction or tradeoff is still unsettled.
- Use `internal-aws-governance` when the next question is IAM, trust, queue policy, or another guardrail design concern.
- Use `internal-aws-operations` when the next question is rollout validation, monitoring, evidence, or recovery proof rather than implementation.
- Use `internal-python-project` when the Lambda code lives in structured Python application modules.
- Use `internal-nodejs-project` when the Lambda code lives in structured Node.js or TypeScript modules.
- Use `internal-terraform` when the primary change is Terraform infrastructure rather than runtime code.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- Run unit tests outside the Lambda runtime and mock AWS boundaries.
- For HTTP handlers, test malformed body, path, query, and error-response cases.
- For queue consumers, test duplicate delivery, poison messages, timeout pressure, and partial batch failure behavior.
- Validate code assumptions together with the deployed timeout, memory, event-source, and queue configuration.
