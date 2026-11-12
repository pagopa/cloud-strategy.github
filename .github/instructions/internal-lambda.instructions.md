---
description: AWS Lambda review checks for handler contracts, input validation, retries and idempotency, limits, IAM scope, and logging.
applyTo: "**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts,**/lambdas/**/*.tf,**/lambdas/**/*.py,**/lambdas/**/*.js,**/lambdas/**/*.ts,**/functions/**/*.tf,**/functions/**/*.py,**/functions/**/*.js,**/functions/**/*.ts"
excludeAgent: "cloud-agent"
---

# Lambda Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify handler signatures and entrypoints are explicit and runtime-correct.
- Flag missing input validation on event payloads and external parameters.
- Check error handling for retry semantics, idempotency, and dead-letter behavior.
- Report business logic coupled directly to platform adapters without seams.
- Verify timeout, memory, and concurrency changes against workload requirements.
- Check IAM scope for least privilege on Lambda execution roles.
- Flag logging that can expose secrets, tokens, or sensitive payload data.
